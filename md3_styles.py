"""
Material Design 3 Styling for OBJ Model Processor
Provides MD3 color system and QSS stylesheets
"""

class MD3Colors:
    """Material Design 3 Color System"""
    
    def __init__(self, theme='light'):
        self.theme = theme
        self.colors = self._get_colors()
    
    def _get_colors(self):
        """Get color palette based on theme"""
        if self.theme == 'light':
            return {
                # Primary colors
                'primary': 'rgb(103, 80, 164)',
                'on_primary': 'rgb(255, 255, 255)',
                'primary_container': 'rgb(234, 221, 255)',
                'on_primary_container': 'rgb(33, 0, 94)',
                
                # Surface colors
                'surface': 'rgb(254, 247, 255)',
                'on_surface': 'rgb(28, 27, 31)',
                'surface_variant': 'rgb(231, 224, 236)',
                'on_surface_variant': 'rgb(73, 69, 78)',
                'surface_container': 'rgb(243, 237, 247)',
                'surface_container_high': 'rgb(236, 230, 240)',
                'surface_container_highest': 'rgb(230, 224, 233)',
                
                # Outline
                'outline': 'rgb(121, 116, 126)',
                'outline_variant': 'rgb(196, 199, 197)',
                
                # Secondary
                'secondary': 'rgb(98, 91, 113)',
                'on_secondary': 'rgb(255, 255, 255)',
                'secondary_container': 'rgb(232, 222, 248)',
                'on_secondary_container': 'rgb(30, 25, 43)',
                
                # Tertiary
                'tertiary': 'rgb(125, 82, 96)',
                'on_tertiary': 'rgb(255, 255, 255)',
                'tertiary_container': 'rgb(255, 216, 228)',
                'on_tertiary_container': 'rgb(55, 11, 30)',
                
                # Error
                'error': 'rgb(179, 38, 30)',
                'on_error': 'rgb(255, 255, 255)',
                'error_container': 'rgb(249, 222, 220)',
                'on_error_container': 'rgb(65, 14, 11)',
                
                # Background
                'background': 'rgb(254, 247, 255)',
                'on_background': 'rgb(28, 27, 31)',
            }
        else:  # dark theme
            return {
                # Primary colors
                'primary': 'rgb(208, 188, 255)',
                'on_primary': 'rgb(55, 30, 115)',
                'primary_container': 'rgb(79, 55, 139)',
                'on_primary_container': 'rgb(234, 221, 255)',
                
                # Surface colors
                'surface': 'rgb(20, 18, 24)',
                'on_surface': 'rgb(230, 225, 229)',
                'surface_variant': 'rgb(73, 69, 79)',
                'on_surface_variant': 'rgb(202, 196, 208)',
                'surface_container': 'rgb(30, 26, 34)',
                'surface_container_high': 'rgb(38, 34, 42)',
                'surface_container_highest': 'rgb(46, 42, 50)',
                
                # Outline
                'outline': 'rgb(147, 143, 153)',
                'outline_variant': 'rgb(73, 69, 79)',
                
                # Secondary
                'secondary': 'rgb(204, 194, 220)',
                'on_secondary': 'rgb(51, 45, 65)',
                'secondary_container': 'rgb(74, 68, 88)',
                'on_secondary_container': 'rgb(232, 222, 248)',
                
                # Tertiary
                'tertiary': 'rgb(239, 184, 200)',
                'on_tertiary': 'rgb(73, 37, 50)',
                'tertiary_container': 'rgb(99, 59, 72)',
                'on_tertiary_container': 'rgb(255, 216, 228)',
                
                # Error
                'error': 'rgb(242, 184, 181)',
                'on_error': 'rgb(105, 0, 5)',
                'error_container': 'rgb(147, 0, 10)',
                'on_error_container': 'rgb(249, 222, 220)',
                
                # Background
                'background': 'rgb(20, 18, 24)',
                'on_background': 'rgb(230, 225, 229)',
            }
    
    def get_main_stylesheet(self):
        """Get complete stylesheet for main application"""
        c = self.colors
        return f"""
            /* Main Window */
            QMainWindow {{
                background-color: {c['background']};
                color: {c['on_background']};
            }}
            
            /* Central Widget */
            QWidget {{
                background-color: {c['surface']};
                color: {c['on_surface']};
                font-family: 'Roboto', 'Segoe UI', sans-serif;
                font-size: 14px;
            }}
            
            /* Labels */
            QLabel {{
                color: {c['on_surface']};
                background: transparent;
            }}
            
            /* Buttons - Filled */
            QPushButton {{
                background-color: {c['primary']};
                color: {c['on_primary']};
                border: none;
                border-radius: 16px;
                padding: 6px 16px;
                font-size: 13px;
                font-weight: 500;
                min-height: 32px;
                max-height: 32px;
            }}
            
            QPushButton:hover {{
                background-color: rgba(103, 80, 164, 0.92);
            }}
            
            QPushButton:pressed {{
                background-color: rgba(103, 80, 164, 0.88);
            }}
            
            QPushButton:disabled {{
                background-color: {c['surface_variant']};
                color: {c['on_surface_variant']};
                opacity: 0.38;
            }}
            
            /* Buttons - Outlined (for secondary actions) */
            QPushButton[class="outlined"] {{
                background-color: transparent;
                color: {c['primary']};
                border: 1px solid {c['outline']};
                border-radius: 16px;
                padding: 6px 16px;
                font-size: 13px;
                font-weight: 500;
                min-height: 32px;
                max-height: 32px;
            }}
            
            QPushButton[class="outlined"]:hover {{
                background-color: rgba(103, 80, 164, 0.08);
            }}
            
            /* Buttons - Text (for tertiary actions) */
            QPushButton[class="text"] {{
                background-color: transparent;
                color: {c['primary']};
                border: none;
                border-radius: 16px;
                padding: 6px 12px;
                font-size: 13px;
                font-weight: 500;
                min-height: 32px;
                max-height: 32px;
            }}
            
            QPushButton[class="text"]:hover {{
                background-color: rgba(103, 80, 164, 0.08);
            }}
            
            /* Group Boxes */
            QGroupBox {{
                background-color: {c['surface_container']};
                border: 1px solid {c['outline_variant']};
                border-radius: 12px;
                margin-top: 12px;
                padding: 16px;
                font-weight: 500;
                color: {c['on_surface']};
            }}
            
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 8px;
                color: {c['on_surface_variant']};
                font-size: 14px;
                font-weight: 500;
            }}
            
            /* List Widget */
            QListWidget {{
                background-color: {c['surface_container']};
                border: 1px solid {c['outline_variant']};
                border-radius: 12px;
                padding: 8px;
                color: {c['on_surface']};
                outline: none;
            }}
            
            QListWidget::item {{
                border-radius: 8px;
                padding: 12px;
                margin: 2px 0;
            }}
            
            QListWidget::item:hover {{
                background-color: rgba(103, 80, 164, 0.08);
            }}
            
            QListWidget::item:selected {{
                background-color: {c['secondary_container']};
                color: {c['on_secondary_container']};
            }}
            
            /* Text Edit */
            QTextEdit {{
                background-color: {c['surface_container']};
                border: 1px solid {c['outline_variant']};
                border-radius: 12px;
                padding: 16px;
                color: {c['on_surface']};
                font-family: 'Roboto Mono', 'Consolas', monospace;
                font-size: 12px;
                selection-background-color: {c['primary_container']};
                selection-color: {c['on_primary_container']};
            }}
            
            /* Checkboxes */
            QCheckBox {{
                color: {c['on_surface']};
                spacing: 8px;
                font-size: 13px;
            }}
            
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border: 2px solid {c['on_surface_variant']};
                border-radius: 2px;
                background-color: transparent;
            }}
            
            QCheckBox::indicator:hover {{
                border-color: {c['primary']};
                background-color: rgba(103, 80, 164, 0.08);
            }}
            
            QCheckBox::indicator:checked {{
                background-color: {c['primary']};
                border-color: {c['primary']};
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTgiIGhlaWdodD0iMTgiIHZpZXdCb3g9IjAgMCAxOCAxOCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cGF0aCBkPSJNNi42IDExLjRMMy4yIDhsLTEuNCAxLjQgNC44IDQuOCA5LjYtOS42TDE0LjggMy4yeiIgZmlsbD0iI2ZmZiIvPjwvc3ZnPg==);
            }}
            
            /* Sliders */
            QSlider::groove:horizontal {{
                background: {c['surface_variant']};
                height: 4px;
                border-radius: 2px;
            }}
            
            QSlider::handle:horizontal {{
                background: {c['primary']};
                width: 20px;
                height: 20px;
                margin: -8px 0;
                border-radius: 10px;
            }}
            
            QSlider::handle:horizontal:hover {{
                background: {c['primary']};
                width: 24px;
                height: 24px;
                margin: -10px 0;
            }}
            
            QSlider::sub-page:horizontal {{
                background: {c['primary']};
                border-radius: 2px;
            }}
            
            /* Progress Bar */
            QProgressBar {{
                background-color: {c['surface_variant']};
                border: none;
                border-radius: 2px;
                height: 4px;
                text-align: center;
            }}
            
            QProgressBar::chunk {{
                background-color: {c['primary']};
                border-radius: 2px;
            }}
            
            /* Splitter */
            QSplitter::handle {{
                background-color: {c['outline_variant']};
                border: 1px solid {c['surface']};
            }}
            
            QSplitter::handle:hover {{
                background-color: {c['outline']};
            }}
            
            /* Menu Bar */
            QMenuBar {{
                background-color: {c['surface']};
                color: {c['on_surface']};
                border-bottom: 1px solid {c['outline_variant']};
                padding: 4px;
            }}
            
            QMenuBar::item {{
                background: transparent;
                padding: 8px 12px;
                border-radius: 8px;
            }}
            
            QMenuBar::item:selected {{
                background-color: rgba(103, 80, 164, 0.08);
            }}
            
            QMenuBar::item:pressed {{
                background-color: {c['primary_container']};
            }}
            
            /* Menu */
            QMenu {{
                background-color: {c['surface_container_high']};
                border: 1px solid {c['outline_variant']};
                border-radius: 12px;
                padding: 8px;
            }}
            
            QMenu::item {{
                padding: 12px 16px;
                border-radius: 8px;
                color: {c['on_surface']};
            }}
            
            QMenu::item:selected {{
                background-color: {c['secondary_container']};
                color: {c['on_secondary_container']};
            }}
            
            /* Status Bar */
            QStatusBar {{
                background-color: {c['surface']};
                color: {c['on_surface_variant']};
                border-top: 1px solid {c['outline_variant']};
                min-height: 28px;
                padding: 4px 8px;
                font-size: 12px;
            }}
            
            QStatusBar::item {{
                border: none;
                padding: 2px 4px;
            }}
            
            /* Scroll Bars */
            QScrollBar:vertical {{
                background: {c['surface']};
                width: 12px;
                border-radius: 6px;
            }}
            
            QScrollBar::handle:vertical {{
                background: {c['outline']};
                border-radius: 6px;
                min-height: 20px;
            }}
            
            QScrollBar::handle:vertical:hover {{
                background: {c['on_surface_variant']};
            }}
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            
            QScrollBar:horizontal {{
                background: {c['surface']};
                height: 12px;
                border-radius: 6px;
            }}
            
            QScrollBar::handle:horizontal {{
                background: {c['outline']};
                border-radius: 6px;
                min-width: 20px;
            }}
            
            QScrollBar::handle:horizontal:hover {{
                background: {c['on_surface_variant']};
            }}
            
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                width: 0px;
            }}
            
            /* Message Box */
            QMessageBox {{
                background-color: {c['surface_container_highest']};
            }}
            
            /* File Dialog */
            QFileDialog {{
                background-color: {c['surface']};
            }}
            
            /* Progress Dialog */
            QProgressDialog {{
                background-color: {c['surface_container_highest']};
                border-radius: 28px;
            }}
        """
    
    def get_toggle_button_stylesheet(self, checked=False, font_size=13):
        """Get stylesheet for toggle button (Full Model / Single Object)"""
        c = self.colors
        scale = font_size / 13  # Scale factor based on font size
        
        if checked:
            return f"""
                QPushButton {{
                    background-color: {c['secondary_container']};
                    color: {c['on_secondary_container']};
                    border: none;
                    border-radius: {int(16 * scale)}px;
                    padding: {int(6 * scale)}px {int(16 * scale)}px;
                    font-size: {font_size}px;
                    font-weight: 500;
                    min-height: {int(32 * scale)}px;
                    max-height: {int(32 * scale)}px;
                }}
                QPushButton:hover {{
                    background-color: rgba(232, 222, 248, 0.92);
                }}
            """
        else:
            return f"""
                QPushButton {{
                    background-color: transparent;
                    color: {c['on_surface_variant']};
                    border: 1px solid {c['outline']};
                    border-radius: {int(16 * scale)}px;
                    padding: {int(6 * scale)}px {int(16 * scale)}px;
                    font-size: {font_size}px;
                    font-weight: 500;
                    min-height: {int(32 * scale)}px;
                    max-height: {int(32 * scale)}px;
                }}
                QPushButton:hover {{
                    background-color: rgba(103, 80, 164, 0.08);
                    border-color: {c['primary']};
                }}
            """


def get_md3_stylesheet(theme='light'):
    """
    Get Material Design 3 stylesheet for the application
    
    Args:
        theme: 'light' or 'dark'
    
    Returns:
        Complete QSS stylesheet string
    """
    colors = MD3Colors(theme)
    return colors.get_main_stylesheet()


def get_md3_colors(theme='light'):
    """
    Get MD3 color palette
    
    Args:
        theme: 'light' or 'dark'
    
    Returns:
        MD3Colors instance
    """
    return MD3Colors(theme)
