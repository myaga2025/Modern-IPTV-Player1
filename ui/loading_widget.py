from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QProgressBar)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QMovie, QPixmap

class LoadingWidget(QWidget):
    """Widget to display a loading animation with status message"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Set up transparent background
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        
        # Create layout
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Loading indicator (either spinner animation or custom progress bar)
        try:
            # Try to load a spinner animation if available
            import os
            spinner_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                  "resources", "icons", "spinner.gif")
            
            if os.path.exists(spinner_path):
                self.loading_label = QLabel()
                self.movie = QMovie(spinner_path)
                self.movie.setScaledSize(QSize(64, 64))
                self.loading_label.setMovie(self.movie)
                layout.addWidget(self.loading_label)
                self.movie.start()
            else:
                # If spinner not found, use a styled progress bar
                self.progress_bar = QProgressBar()
                self.progress_bar.setRange(0, 0)  # Indeterminate mode
                self.progress_bar.setTextVisible(False)
                self.progress_bar.setMinimumWidth(200)
                self.progress_bar.setStyleSheet("""
                    QProgressBar {
                        border: 2px solid #0078D7;
                        border-radius: 5px;
                        background-color: rgba(40, 40, 40, 180);
                        height: 20px;
                    }
                    QProgressBar::chunk {
                        background-color: #0078D7;
                        width: 10px;
                    }
                """)
                layout.addWidget(self.progress_bar)
        except Exception as e:
            print(f"Error setting up loading animation: {e}")
            # Fallback to simple progress bar
            self.progress_bar = QProgressBar()
            self.progress_bar.setRange(0, 0)  # Indeterminate mode
            layout.addWidget(self.progress_bar)
        
        # Status message
        self.status_label = QLabel("جاري التحميل...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: white; font-size: 14px; font-weight: bold; background-color: rgba(0, 0, 0, 0);")
        layout.addWidget(self.status_label)
        
        # Set widget style
        self.setStyleSheet("""
            LoadingWidget {
                background-color: rgba(0, 0, 0, 100);
                border-radius: 10px;
            }
        """)
        
    def set_message(self, message):
        """Update the status message"""
        self.status_label.setText(message)
        
    def set_progress(self, value, maximum=100):
        """Update progress bar if it exists and is determinate"""
        if hasattr(self, 'progress_bar') and self.progress_bar.maximum() > 0:
            self.progress_bar.setValue(value)
            self.progress_bar.setMaximum(maximum)
    
    def make_determinate(self, maximum=100):
        """Convert progress bar to determinate mode if it exists"""
        if hasattr(self, 'progress_bar'):
            self.progress_bar.setRange(0, maximum)
            self.progress_bar.setValue(0)
    
    def make_indeterminate(self):
        """Convert progress bar to indeterminate mode if it exists"""
        if hasattr(self, 'progress_bar'):
            self.progress_bar.setRange(0, 0)
    
    def showEvent(self, event):
        """Handle show event to center widget on parent"""
        super().showEvent(event)
        if self.parent():
            # Center on parent
            parent_rect = self.parent().rect()
            self.move(
                parent_rect.center().x() - self.width() // 2,
                parent_rect.center().y() - self.height() // 2
            )
