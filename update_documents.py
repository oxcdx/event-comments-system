#!/usr/bin/env python3
"""
Script to update database documents with current HTML file content
"""
import sqlite3
import os
import sys

def update_documents():
    """Update documents in database with current HTML file content"""
    
    # Document mappings
    documents = [
        {
            'id': 'hyperlocal-hotspot',
            'title': 'Hyperlocal Hotspot – Compiler',
            'file': 'hyperlocal-hotspot.html'
        },
        {
            'id': 'planetary-design',
            'title': 'Planetary Design: On the emerging logics of Generative AI – Orit Halpern',
            'file': 'planetary-design.html'
        },
        {
            'id': 'diffractive-politics',
            'title': 'Diffractive Politics: Accelerationism, Computation, & the Political – Ezekiel Dixon-Román',
            'file': 'diffractive-politics.html'
        },
        {
            'id': 'infrastructures-political-values',
            'title': 'Infrastructures of Political Values – Connal Parsley',
            'file': 'infrastructures-political-values.html'
        },
        {
            'id': 'infrastructuring-architecture',
            'title': 'Infrastructuring Architecture Knowledge – Sol Pérez Martínez',
            'file': 'infrastructuring-architecture.html'
        },
        {
            'id': 'sustainable-ai',
            'title': 'Reimagining AI and IT for Sustainable Infrastructure',
            'file': 'sustainable-ai.html'
        },
        {
            'id': 'discussion',
            'title': 'Discussion Session',
            'file': 'discussion.html'
        }
    ]
    
    # Connect to database
    conn = sqlite3.connect('annotations.db')
    cursor = conn.cursor()
    
    for doc in documents:
        file_path = f"documents/{doc['file']}"
        
        if os.path.exists(file_path):
            try:
                # Read current content from file
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Update document in database
                cursor.execute('''
                    UPDATE documents 
                    SET content = ?, title = ?
                    WHERE id = ?
                ''', (content, doc['title'], doc['id']))
                
                if cursor.rowcount > 0:
                    print(f"✓ Updated: {doc['title']}")
                else:
                    print(f"⚠ Document not found in DB: {doc['id']}")
                    
            except Exception as e:
                print(f"✗ Error updating {doc['file']}: {e}")
        else:
            print(f"✗ File not found: {file_path}")
    
    # Commit changes
    conn.commit()
    conn.close()
    print("\nDatabase update complete!")

if __name__ == "__main__":
    update_documents()
