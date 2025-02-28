#!/usr/bin/env python3
"""
Simple HTTP server to serve the static frontend files during development.
This allows testing the frontend integration with the backend API.
"""

import http.server
import socketserver
import os
import webbrowser
from urllib.parse import urlparse

# Configuration
PORT = 3000
DIRECTORY = "."

class Handler(http.server.SimpleHTTPRequestHandler):
    """Custom request handler that serves files from the static directory."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)
    
    def log_message(self, format, *args):
        """Override to provide more informative logging."""
        path = urlparse(self.path).path
        print(f"{self.log_date_time_string()} - {self.address_string()} - {self.command} {path} {args[0]}")

def main():
    """Start the server and open the browser."""
    # Change to the script's directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Ensure the static directory exists
    if not os.path.isdir(DIRECTORY):
        print(f"Error: '{DIRECTORY}' directory not found.")
        return
    
    # Create the server
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Serving frontend at http://localhost:{PORT}")
        print(f"Press Ctrl+C to stop the server")
        
        # Open browser
        webbrowser.open(f"http://localhost:{PORT}/index.html")
        
        # Serve until interrupted
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")

if __name__ == "__main__":
    main()
