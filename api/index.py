import sys
import os

# Add root folder to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app

app = create_app()
