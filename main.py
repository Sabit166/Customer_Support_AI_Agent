"""
Customer Support AI Agent - Main Entry Point
This module serves as the primary entry point for the Customer Support AI Agent application.
"""

import os
import sys
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from src.interfaces.streamlit_app import main as streamlit_main
from src.interfaces.cli_interface import main as cli_main
from src.utils.config import Config
from src.utils.logger import setup_logging

def main():
    """Main application entry point"""
    # Setup logging
    setup_logging()
    
    # Load configuration
    config = Config()
    
    # Check for command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == "--cli":
        # Run CLI interface
        cli_main()
    else:
        # Default to Streamlit web interface
        print("🚀 Starting Customer Support AI Agent...")
        print("📱 Web interface will open in your browser")
        streamlit_main()

if __name__ == "__main__":
    main()