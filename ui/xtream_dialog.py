from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QLineEdit, QFormLayout, QMessageBox,
                           QApplication, QCheckBox, QDialogButtonBox, QProgressBar)
from PyQt6.QtCore import Qt, pyqtSignal, QThread, QObject, QTimer
from core.language_manager import tr
from core.xtream_client import XtreamClient
import os
import time

class XtreamConnectionThread(QObject):
    """Thread for Xtream connection to prevent UI freezing"""
    progress_updated = pyqtSignal(int, str)  # Progress value, status message
    connection_result = pyqtSignal(bool, str, object, list)  # Success, message, client, streams
    chunk_data_ready = pyqtSignal(list)  # Signal to emit when a chunk of data is ready
    
    def __init__(self):
        super().__init__()
        self._running = False
        self._max_chunk_size = 100  # Maximum number of streams to process in one chunk
    
    def connect(self, server, username, password):
        """Connect to Xtream server in a separate thread"""
        if self._running:
            return
            
        self._running = True
        
        # Create the client and attempt connection
        try:
            self.progress_updated.emit(10, tr("جاري الاتصال بالخادم..."))
            client = XtreamClient(server, username, password)
            
            # Connect to server
            success, message = client.connect()
            
            if not success or not self._running:
                self.connection_result.emit(False, message, None, [])
                self._running = False
                return
                
            self.progress_updated.emit(30, tr("جاري تحميل الفئات..."))
            time.sleep(0.2)  # Small delay for progress bar visibility
            
            # Get categories
            categories = client.get_live_categories()
            
            if not self._running:
                self.connection_result.emit(False, "Cancelled", None, [])
                self._running = False
                return
                
            self.progress_updated.emit(50, tr("جاري تحميل القنوات..."))
            
            # Get live streams - we'll process them in chunks to avoid freezing
            streams = client.get_live_streams()
            
            if not self._running:
                self.connection_result.emit(False, "Cancelled", None, [])
                self._running = False
                return
                
            # إذا كان لدينا الكثير من المحتوى، نقوم بتقسيمه إلى دفعات للتحميل التدريجي
            if len(streams) > self._max_chunk_size:
                # تقسيم المحتوى إلى دفعات وإرسالها تدريجيًا
                num_chunks = (len(streams) + self._max_chunk_size - 1) // self._max_chunk_size  # عدد الدفعات المطلوبة
                progress_start = 50
                progress_end = 80
                progress_step = (progress_end - progress_start) / num_chunks
                
                for i in range(0, len(streams), self._max_chunk_size):
                    if not self._running:
                        self.connection_result.emit(False, "Cancelled", None, [])
                        self._running = False
                        return
                        
                    # حساب نسبة التقدم الحالية
                    current_chunk = i // self._max_chunk_size
                    current_progress = int(progress_start + (current_chunk * progress_step))
                    self.progress_updated.emit(current_progress, tr(f"جاري تحميل القنوات... {current_chunk+1}/{num_chunks}"))
                    
                    # إرسال دفعة من البيانات
                    chunk = streams[i:i + self._max_chunk_size]
                    self.chunk_data_ready.emit(chunk)
                    
                    # إضافة تأخير صغير لإتاحة الفرصة للواجهة للتحديث
                    time.sleep(0.05)
            
            self.progress_updated.emit(80, tr("جاري تحميل بيانات المستخدم..."))
            time.sleep(0.2)  # Small delay for progress bar visibility
            
            # Get VOD categories
            client.get_vod_categories()
            
            if not self._running:
                self.connection_result.emit(False, "Cancelled", None, [])
                self._running = False
                return
                
            self.progress_updated.emit(90, tr("جاري إنهاء الاتصال..."))
            time.sleep(0.2)  # Small delay for progress bar visibility
            
            if streams:
                self.connection_result.emit(True, "Connection successful", client, streams)
            else:
                self.connection_result.emit(False, tr("Connected, but no streams were found"), client, [])
                
        except Exception as e:
            self.connection_result.emit(False, str(e), None, [])
        finally:
            self._running = False
            self.progress_updated.emit(100, tr("اكتمل!"))
    
    def stop(self):
        """Stop the connection process"""
        self._running = False

class XtreamLoginDialog(QDialog):
    """Dialog for Xtream API login"""
    
    # Signal emitted when a successful connection is made
    connection_successful = pyqtSignal(dict, list)
    # Signal to emit chunks of data to the parent
    data_chunk_ready = pyqtSignal(list)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.client = None
        self.connection_thread = None
        self.worker_thread = None
        self.received_streams = []  # لتجميع الدفعات المستلمة
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the dialog UI"""
        self.setWindowTitle(tr("Xtream Connection"))
        self.setMinimumWidth(450)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        
        # Get theme colors
        app = QApplication.instance()
        is_dark_theme = app and app.styleSheet() and "background-color: #121212" in app.styleSheet()
        text_color = "#FFFFFF" if is_dark_theme else "#000000"
        accent_color = "#0078D7"
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title_label = QLabel(tr("Connect to Xtream Provider"))
        title_label.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {accent_color};")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Form for server details
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        
        # Server URL
        self.server_input = QLineEdit()
        self.server_input.setPlaceholderText("example.com:8080")
        form_layout.addRow(tr("Server URL:"), self.server_input)
        
        # Username
        self.username_input = QLineEdit()
        form_layout.addRow(tr("Username:"), self.username_input)
        
        # Password
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addRow(tr("Password:"), self.password_input)
        
        main_layout.addLayout(form_layout)
        
        # Remember credentials checkbox
        self.remember_checkbox = QCheckBox(tr("Remember credentials"))
        self.remember_checkbox.setChecked(True)
        main_layout.addWidget(self.remember_checkbox)
        
        # Progress bar (initially hidden)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.hide()
        main_layout.addWidget(self.progress_bar)
        
        # Status message
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #0078D7; font-weight: bold;")
        self.status_label.setWordWrap(True)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.status_label)
        
        # Create button box
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | 
                                          QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.connect_to_server)
        self.button_box.rejected.connect(self.reject)
        self.button_box.button(QDialogButtonBox.StandardButton.Ok).setText(tr("Connect"))
        self.button_box.button(QDialogButtonBox.StandardButton.Cancel).setText(tr("Cancel"))
        
        # Store reference to the connect button
        self.connect_button = self.button_box.button(QDialogButtonBox.StandardButton.Ok)
        
        main_layout.addWidget(self.button_box)
        
        # Create connection thread object
        self.connection_thread = XtreamConnectionThread()
        self.connection_thread.progress_updated.connect(self.update_progress)
        self.connection_thread.connection_result.connect(self.process_connection_result)
        self.connection_thread.chunk_data_ready.connect(self.process_data_chunk)
        
        # Load any saved credentials
        self.load_saved_credentials()
    
    def load_saved_credentials(self):
        """Load saved credentials if available"""
        try:
            data_dir = os.path.join(os.environ.get('APPDATA', os.path.expanduser('~')), 
                               'Modern-IPTV-Player', 'data')
            credentials_file = os.path.join(data_dir, 'xtream_credentials.txt')
            
            if os.path.exists(credentials_file):
                with open(credentials_file, 'r') as f:
                    lines = f.readlines()
                    if len(lines) >= 3:
                        self.server_input.setText(lines[0].strip())
                        self.username_input.setText(lines[1].strip())
                        self.password_input.setText(lines[2].strip())
        except Exception as e:
            print(f"Error loading saved credentials: {str(e)}")
    
    def save_credentials(self, server, username, password):
        """Save credentials if remember checkbox is checked"""
        if self.remember_checkbox.isChecked():
            try:
                data_dir = os.path.join(os.environ.get('APPDATA', os.path.expanduser('~')), 
                                   'Modern-IPTV-Player', 'data')
                os.makedirs(data_dir, exist_ok=True)
                credentials_file = os.path.join(data_dir, 'xtream_credentials.txt')
                
                with open(credentials_file, 'w') as f:
                    f.write(f"{server}\n{username}\n{password}")
            except Exception as e:
                print(f"Error saving credentials: {str(e)}")
    
    def update_progress(self, value, message):
        """Update the progress bar and status message"""
        self.progress_bar.setValue(value)
        self.status_label.setText(message)
    
    def connect_to_server(self):
        """Attempt to connect to the Xtream server"""
        server = self.server_input.text().strip()
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        if not server or not username or not password:
            self.status_label.setText(tr("Please fill in all fields"))
            self.status_label.setStyleSheet("color: red;")
            return
        
        # Show progress bar and status
        self.progress_bar.show()
        self.progress_bar.setValue(0)
        self.status_label.setStyleSheet("color: #0078D7; font-weight: bold;")
        self.status_label.setText(tr("جاري الاتصال..."))
        
        # Disable form controls during connection
        self.setFormEnabled(False)
        
        # Create a new thread for the connection
        if self.worker_thread is not None:
            # Clean up previous thread if it exists
            if self.worker_thread.isRunning():
                self.connection_thread.stop()
                self.worker_thread.quit()
                self.worker_thread.wait(1000)  # Wait for the thread to finish
        
        # Create a fresh thread
        self.worker_thread = QThread()
        self.connection_thread.moveToThread(self.worker_thread)
        self.worker_thread.started.connect(lambda: self.connection_thread.connect(server, username, password))
        self.worker_thread.start()
    
    def setFormEnabled(self, enabled):
        """Enable or disable form controls during connection"""
        self.server_input.setEnabled(enabled)
        self.username_input.setEnabled(enabled)
        self.password_input.setEnabled(enabled)
        self.remember_checkbox.setEnabled(enabled)
        self.connect_button.setEnabled(enabled)
    
    def process_connection_result(self, success, message, client, streams):
        """Process the result of the connection attempt"""
        if success:
            server = self.server_input.text().strip()
            username = self.username_input.text().strip()
            password = self.password_input.text().strip()
            
            self.save_credentials(server, username, password)
            
            # Create connection info to return
            info = {
                'server': server,
                'username': username,
                'password': password,
                'status': client.user_info.get('status', 'Active'),
                'expiry': client.user_info.get('exp_date', 'Unknown'),
                'user_info': client.user_info,
                'server_info': client.server_info
            }
            
            # Emit signal with connection info and received channels
            self.connection_successful.emit(info, streams)
            self.accept()
        else:
            # Re-enable form
            self.setFormEnabled(True)
            
            # Update status with error message
            self.status_label.setText(message)
            self.status_label.setStyleSheet("color: red;")
            
            # Hide progress bar
            self.progress_bar.hide()
    
    def process_data_chunk(self, chunk):
        """معالجة دفعة من البيانات المستلمة"""
        # إضافة هذه الدفعة إلى القائمة الإجمالية
        self.received_streams.extend(chunk)
        
        # إمكانية إرسال الدفعة إلى المكون الأصلي لتحديث الواجهة تدريجيًا
        self.data_chunk_ready.emit(chunk)
        
        # تحديث حالة العرض للمستخدم
        self.status_label.setText(tr(f"تم استلام {len(self.received_streams)} قناة..."))
        
        # السماح لحلقة أحداث Qt بالمعالجة
        QApplication.processEvents()
    
    def reject(self):
        """Override reject to stop the connection thread"""
        if hasattr(self, 'connection_thread'):
            self.connection_thread.stop()
        
        # Clean up thread
        if hasattr(self, 'worker_thread') and self.worker_thread is not None:
            if self.worker_thread.isRunning():
                self.worker_thread.quit()
                self.worker_thread.wait(1000)  # Wait up to 1 second for thread to finish
        
        super().reject()
    
    def closeEvent(self, event):
        """Handle window close event"""
        self.reject()
        super().closeEvent(event)
    
    def __del__(self):
        """Clean up resources when the dialog is deleted"""
        # Ensure threads are stopped when this object is deleted
        if hasattr(self, 'connection_thread'):
            self.connection_thread.stop()
        
        if hasattr(self, 'worker_thread') and self.worker_thread is not None:
            if self.worker_thread.isRunning():
                self.worker_thread.quit()
                self.worker_thread.wait(1000)  # Wait up to 1 second for thread to finish


class XtreamInfoDialog(QDialog):
    """Dialog to display Xtream connection information"""
    
    def __init__(self, connection_info, parent=None):
        super().__init__(parent)
        self.connection_info = connection_info
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the dialog UI"""
        self.setWindowTitle(tr("Xtream Connection Info"))
        self.setMinimumWidth(400)
        
        # Get theme colors
        app = QApplication.instance()
        is_dark_theme = app and app.styleSheet() and "background-color: #121212" in app.styleSheet()
        text_color = "#FFFFFF" if is_dark_theme else "#000000"
        secondary_text = "#AAAAAA" if is_dark_theme else "#555555"
        accent_color = "#0078D7"
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        
        # Title
        title_label = QLabel(tr("Connection Information"))
        title_label.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {accent_color};")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Server info
        server_label = QLabel(tr("Server:"))
        server_label.setStyleSheet(f"font-weight: bold; color: {text_color};")
        server_value = QLabel(self.connection_info.get('server', 'Unknown'))
        server_value.setStyleSheet(f"color: {secondary_text};")
        
        # Username info
        user_label = QLabel(tr("Username:"))
        user_label.setStyleSheet(f"font-weight: bold; color: {text_color};")
        user_value = QLabel(self.connection_info.get('username', 'Unknown'))
        user_value.setStyleSheet(f"color: {secondary_text};")
        
        # Status info
        status_label = QLabel(tr("Status:"))
        status_label.setStyleSheet(f"font-weight: bold; color: {text_color};")
        status_value = QLabel(self.connection_info.get('status', 'Unknown'))
        status_value.setStyleSheet(f"color: {secondary_text};")
        
        # Expiry info
        expiry_label = QLabel(tr("Expiration:"))
        expiry_label.setStyleSheet(f"font-weight: bold; color: {text_color};")
        
        # Convert timestamp to readable date if needed
        expiry = self.connection_info.get('expiry', 'Unknown')
        if expiry and expiry.isdigit():
            from datetime import datetime
            try:
                dt = datetime.fromtimestamp(int(expiry))
                expiry = dt.strftime('%Y-%m-%d %H:%M')
            except:
                pass
                
        expiry_value = QLabel(expiry)
        expiry_value.setStyleSheet(f"color: {secondary_text};")
        
        # Create form layout for the info
        form_layout = QFormLayout()
        form_layout.addRow(server_label, server_value)
        form_layout.addRow(user_label, user_value)
        form_layout.addRow(status_label, status_value)
        form_layout.addRow(expiry_label, expiry_value)
        main_layout.addLayout(form_layout)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        button_box.accepted.connect(self.accept)
        main_layout.addWidget(button_box)
