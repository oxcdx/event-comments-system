# Text Annotator - Technical Documentation

## Architecture Overview

The Text Annotator uses a **non-destructive overlay approach** to display highlights and annotations without modifying the original document structure.

## Key Features

### Safe Highlighting System
- **No DOM Modification**: The original document HTML is never altered
- **CSS Overlays**: Highlights are positioned absolutely over the text
- **Overlap Support**: Multiple annotations can overlap without corruption
- **Responsive**: Highlights reposition automatically on window resize

### Real-time Collaboration
- **WebSocket Communication**: Instant updates across all connected users
- **SQLite Database**: Persistent storage of all annotations
- **User Attribution**: Each annotation tracks the author
- **Color Coding**: Different colors for different users/types

## How It Works

### 1. Text Selection
- User selects text in the document
- JavaScript calculates character offsets from the beginning of the document
- Offsets are stored in the database with the annotation

### 2. Highlight Rendering
- `createRangeFromTextOffset()` converts stored offsets back to DOM ranges
- `getClientRects()` gets the precise pixel coordinates of the text
- Absolute positioned `<div>` elements are created as overlays
- Comment markers (💬) are positioned next to annotated text

### 3. Collision Handling
- Multiple overlapping annotations are rendered independently
- Each annotation has its own overlay element
- CSS opacity allows overlapping highlights to blend naturally
- Click handlers work through the overlay system

## File Structure

```
/home/copmiler-ox/text-annotator/
├── app.py                    # Flask application with WebSocket support
├── requirements.txt          # Python dependencies
├── annotations.db           # SQLite database (auto-created)
├── templates/
│   ├── index.html           # Home page
│   └── document.html        # Document viewer with annotation system
├── venv/                    # Python virtual environment
├── manage.sh                # Management script
├── nginx-text-annotator.conf # Nginx configuration
└── text-annotator.service  # Systemd service file
```

## Database Schema

### documents table
- `id` (TEXT PRIMARY KEY)
- `title` (TEXT NOT NULL)
- `content` (TEXT NOT NULL) - Original HTML content
- `created_at` (DATETIME)

### annotations table
- `id` (TEXT PRIMARY KEY)
- `text_id` (TEXT) - References document.id
- `start_offset` (INTEGER) - Character position start
- `end_offset` (INTEGER) - Character position end
- `selected_text` (TEXT) - The actual selected text
- `comment` (TEXT) - Optional comment
- `author` (TEXT) - User who created the annotation
- `color` (TEXT) - Highlight color
- `timestamp` (DATETIME)

## API Endpoints

### Web Routes
- `GET /` - Home page
- `GET /document/<doc_id>` - Document viewer
- `GET /api/annotations/<text_id>` - Get annotations for a document

### WebSocket Events
- `join_document` - Join a document room for real-time updates
- `leave_document` - Leave a document room
- `add_annotation` - Create a new annotation
- `remove_annotation` - Delete an annotation
- `new_annotation` - Broadcast new annotation to all users
- `annotation_removed` - Broadcast annotation removal

## System Requirements

- Python 3.11+
- Nginx (reverse proxy)
- SQLite (built-in)
- Modern web browser with WebSocket support

## Management Commands

```bash
# Check status
./manage.sh status

# View logs
./manage.sh logs

# Restart services
./manage.sh restart

# Stop services
./manage.sh stop

# Start services
./manage.sh start
```

## Security Considerations

- Input sanitization in both Python and JavaScript
- XSS prevention through proper HTML escaping
- SQLite injection prevention using parameterized queries
- CORS handling for WebSocket connections

## Performance Notes

- Overlay rendering is optimized for smooth scrolling
- Database queries are minimal and indexed
- WebSocket events are efficiently broadcast only to document subscribers
- CSS transforms used for smooth highlight positioning

## Troubleshooting

### Common Issues
1. **Highlights not appearing**: Check browser console for JavaScript errors
2. **Real-time not working**: Verify WebSocket connection in Network tab
3. **Service not starting**: Check `sudo journalctl -u text-annotator`
4. **Nginx errors**: Check `sudo journalctl -u nginx`

### Reset Database
```bash
cd /home/copmiler-ox/text-annotator
rm -f annotations.db
sudo systemctl restart text-annotator
```

## Accessing the Application

- **Local**: http://localhost:8080
- **Network**: http://192.168.0.111:8080
- **Sample Document**: http://192.168.0.111:8080/document/sample
