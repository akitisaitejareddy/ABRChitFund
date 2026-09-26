import sys
import os

# Set root directory in sys.path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from app import create_app

app = create_app()

# Expose WSGI handler for Vercel
if __name__ == '__main__':
    app.run()
