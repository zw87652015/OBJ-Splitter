#!/usr/bin/env python3
"""
Simple PyQt6 Test Script
Tests if PyQt6 is properly installed and running on the system.
"""

import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QVBoxLayout, QWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont


class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt6 Test - Working!")
        self.setGeometry(100, 100, 400, 300)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Add title label
        title_label = QLabel("PyQt6 Test Successful!")
        title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Add info label
        info_label = QLabel("PyQt6 is installed and working correctly.")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info_label)
        
        # Add version info
        try:
            from PyQt6 import QtCore
            version_label = QLabel(f"PyQt6 Version: {QtCore.QT_VERSION_STR}")
            version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(version_label)
        except ImportError:
            version_label = QLabel("Could not retrieve PyQt6 version info")
            version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(version_label)
        
        # Add test button
        test_button = QPushButton("Test Button Click")
        test_button.clicked.connect(self.on_button_click)
        layout.addWidget(test_button)
        
        # Add status label
        self.status_label = QLabel("Ready")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
    
    def on_button_click(self):
        self.status_label.setText("Button clicked successfully!")


def main():
    print("Testing PyQt6 installation...")
    
    # Create QApplication
    app = QApplication(sys.argv)
    
    # Create and show test window
    window = TestWindow()
    window.show()
    
    print("PyQt6 test window launched successfully!")
    print("If you can see the window, PyQt6 is working correctly.")
    
    # Run the application
    sys.exit(app.exec())


if __name__ == "__main__":
    try:
        main()
    except ImportError as e:
        print(f"Error: {e}")
        print("PyQt6 is not installed. Please install it with:")
        print("pip install PyQt6")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)
