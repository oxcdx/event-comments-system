#!/usr/bin/env python3
"""
Script to verify that the text annotator app is completely offline-ready.
Checks for any external dependencies in HTML files.
"""

import os
import re
from pathlib import Path

def check_file_for_external_deps(file_path):
    """Check a single file for external dependencies."""
    print(f"\nChecking {file_path}...")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Patterns to look for external dependencies
    patterns = [
        (r'https?://[^"\'>\s]+', 'External URL'),
        (r'<script[^>]+src=["\']https?://[^"\']+["\']', 'External JavaScript'),
        (r'<link[^>]+href=["\']https?://[^"\']+["\']', 'External CSS'),
        (r'@import\s+url\(["\']?https?://[^"\')\s]+["\']?\)', 'External CSS Import'),
    ]
    
    found_external = False
    for pattern, desc in patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        if matches:
            found_external = True
            print(f"  ⚠️  Found {desc}:")
            for match in matches:
                print(f"    - {match}")
    
    if not found_external:
        print("  ✅ No external dependencies found")
    
    return not found_external

def main():
    """Main function to check all relevant files."""
    print("🔍 Checking Text Annotator for offline readiness...")
    
    # Files to check
    files_to_check = [
        'templates/index.html',
        'templates/document.html'
    ]
    
    all_offline = True
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            is_offline = check_file_for_external_deps(file_path)
            all_offline = all_offline and is_offline
        else:
            print(f"⚠️  File not found: {file_path}")
            all_offline = False
    
    print(f"\n{'='*50}")
    if all_offline:
        print("✅ SUCCESS: Application is completely offline-ready!")
        print("📱 The app will work without internet connection.")
    else:
        print("❌ FAILED: Application has external dependencies!")
        print("🌐 Internet connection may be required.")
    
    # Check for local static files
    print(f"\n📁 Static files check:")
    static_files = [
        'static/js/socket.io.min.js'
    ]
    
    for file_path in static_files:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            print(f"  ✅ {file_path} ({size:,} bytes)")
        else:
            print(f"  ❌ Missing: {file_path}")
            all_offline = False
    
    print(f"\n{'='*50}")
    if all_offline:
        print("🎉 FINAL RESULT: Application is 100% offline-ready!")
    else:
        print("🔧 FINAL RESULT: Some issues need to be fixed for full offline support.")

if __name__ == "__main__":
    main()
