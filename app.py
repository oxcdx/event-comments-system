from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
import sqlite3
import uuid
import json
import logging
from datetime import datetime
import threading

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-change-this'
socketio = SocketIO(app, cors_allowed_origins="*")

# Database initialization
def init_db():
    conn = sqlite3.connect('annotations.db')
    cursor = conn.cursor()
    
    # Create annotations table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS annotations (
            id TEXT PRIMARY KEY,
            text_id TEXT NOT NULL,
            start_offset INTEGER NOT NULL,
            end_offset INTEGER NOT NULL,
            selected_text TEXT NOT NULL,
            comment TEXT,
            author TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            color TEXT DEFAULT '#ffff00',
            session_id TEXT
        )
    ''')
    
    # Create documents table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS documents (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect('annotations.db')
    conn.row_factory = sqlite3.Row
    return conn

# Initialize database on startup
init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/document/<doc_id>')
def document(doc_id):
    conn = get_db_connection()
    document = conn.execute('SELECT * FROM documents WHERE id = ?', (doc_id,)).fetchone()
    annotations_rows = conn.execute('SELECT * FROM annotations WHERE text_id = ? ORDER BY start_offset', (doc_id,)).fetchall()
    conn.close()
    
    # Convert Row objects to dictionaries
    annotations = [dict(row) for row in annotations_rows]
    
    if document:
        return render_template('document.html', document=document, annotations=annotations)
    else:
        # Create a sample document if none exists
        sample_content = """
        <h1>Sample Document for Annotation</h1>
        <p>This is a sample document that demonstrates the text annotation system. You can select any text in this document and add comments or highlights that will be visible to all users in real-time.</p>
        
        <p>The annotation system supports:</p>
        <ul>
            <li>Real-time highlighting of selected text</li>
            <li>Collaborative commenting on text selections</li>
            <li>Persistent storage of all annotations</li>
            <li>Color-coded highlights for different types of annotations</li>
        </ul>
        
        <p>To use the system, simply select any text and choose to either highlight it or add a comment. Your annotations will be immediately visible to all other users viewing this document.</p>
        
        <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p>
        """
        
        conn = get_db_connection()
        conn.execute('INSERT INTO documents (id, title, content) VALUES (?, ?, ?)', 
                    (doc_id, 'Sample Document', sample_content))
        conn.commit()
        document = conn.execute('SELECT * FROM documents WHERE id = ?', (doc_id,)).fetchone()
        annotations = []
        conn.close()
        
        return render_template('document.html', document=document, annotations=annotations)

@app.route('/api/annotations/<text_id>')
def get_annotations(text_id):
    conn = get_db_connection()
    annotations_rows = conn.execute('SELECT * FROM annotations WHERE text_id = ? ORDER BY start_offset', (text_id,)).fetchall()
    conn.close()
    
    # Convert Row objects to dictionaries
    annotations = [dict(row) for row in annotations_rows]
    
    return jsonify(annotations)

@socketio.on('join_document')
def on_join(data):
    doc_id = data['doc_id']
    join_room(doc_id)
    emit('status', {'msg': f'User joined document {doc_id}'}, room=doc_id)

@socketio.on('leave_document')
def on_leave(data):
    doc_id = data['doc_id']
    leave_room(doc_id)
    emit('status', {'msg': f'User left document {doc_id}'}, room=doc_id)

@socketio.on('add_annotation')
def handle_annotation(data):
    try:
        annotation_id = str(uuid.uuid4())
        doc_id = data['doc_id']
        start_offset = data['start_offset']
        end_offset = data['end_offset']
        selected_text = data['selected_text']
        comment = data.get('comment', '')
        author = data.get('author', 'Anonymous')
        color = data.get('color', '#ffff00')
        session_id = data.get('session_id', '')
        
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO annotations (id, text_id, start_offset, end_offset, selected_text, comment, author, color, session_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (annotation_id, doc_id, start_offset, end_offset, selected_text, comment, author, color, session_id))
        conn.commit()
        conn.close()
        
        # Broadcast the new annotation to all users in the document room
        emit('new_annotation', {
            'id': annotation_id,
            'text_id': doc_id,
            'start_offset': start_offset,
            'end_offset': end_offset,
            'selected_text': selected_text,
            'comment': comment,
            'author': author,
            'color': color,
            'session_id': session_id,
            'timestamp': datetime.now().isoformat()
        }, room=doc_id)
        
    except Exception as e:
        logger.error(f'Error adding annotation: {e}')
        emit('error', {'message': 'Failed to add annotation'})

@socketio.on('edit_annotation')
def handle_edit_annotation(data):
    try:
        annotation_id = data['annotation_id']
        new_comment = data['new_comment']
        doc_id = data['doc_id']
        
        # Get session_id from request context or data
        session_id = data.get('session_id')
        if not session_id:
            emit('error', {'message': 'Session ID required'})
            return
        
        conn = get_db_connection()
        # Only allow editing if session_id matches
        result = conn.execute('UPDATE annotations SET comment = ? WHERE id = ? AND session_id = ?', 
                             (new_comment, annotation_id, session_id))
        
        if result.rowcount > 0:
            conn.commit()
            # Broadcast the updated annotation to all users in the document room
            emit('annotation_edited', {
                'annotation_id': annotation_id,
                'new_comment': new_comment
            }, room=doc_id)
        else:
            emit('error', {'message': 'You can only edit your own annotations'})
            
        conn.close()
        
    except Exception as e:
        logger.error(f'Error editing annotation: {e}')
        emit('error', {'message': 'Failed to edit annotation'})
@socketio.on('remove_annotation')
def handle_remove_annotation(data):
    try:
        annotation_id = data['annotation_id']
        doc_id = data['doc_id']
        
        # Get session_id from request context or data
        session_id = data.get('session_id')
        if not session_id:
            emit('error', {'message': 'Session ID required'})
            return
        
        conn = get_db_connection()
        # Only allow deletion if session_id matches
        result = conn.execute('DELETE FROM annotations WHERE id = ? AND session_id = ?', 
                             (annotation_id, session_id))
        
        if result.rowcount > 0:
            conn.commit()
            # Broadcast the annotation removal to all users in the document room
            emit('annotation_removed', {'annotation_id': annotation_id}, room=doc_id)
        else:
            emit('error', {'message': 'You can only delete your own annotations'})
            
        conn.close()
        
    except Exception as e:
        logger.error(f'Error removing annotation: {e}')
        emit('error', {'message': 'Failed to remove annotation'})

# Add error handlers
@app.errorhandler(500)
def internal_error(error):
    logger.error(f'Internal Server Error: {error}')
    return 'Internal Server Error - Please check the application logs', 500

@app.errorhandler(404)
def not_found(error):
    return 'Page not found', 404

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
