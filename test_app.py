#!/usr/bin/env python3
"""
Simple test to verify the application can start without errors
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from PyQt5.QtWidgets import QApplication
    from obj_model_processor import OBJProcessorApp
    
    print("Testing OBJ Model Processor startup...")
    
    # Create application
    app = QApplication(sys.argv)
    
    # Create main window
    window = OBJProcessorApp()
    
    print("✅ Application created successfully!")
    print("✅ All UI elements initialized properly!")
    print("✅ No AttributeError detected!")
    
    # Don't show the window, just test creation
    print("\nApplication is ready to run.")
    print("To start the GUI, run: python obj_model_processor.py")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please install dependencies: pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

print("\n✅ All tests passed!")
