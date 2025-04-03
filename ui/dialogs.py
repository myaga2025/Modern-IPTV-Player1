from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                           QLineEdit, QPushButton, QComboBox, QDialogButtonBox,
                           QTextBrowser, QListWidget, QListWidgetItem, QInputDialog,
                           QMessageBox, QTabWidget, QGroupBox, QWidget, QTextEdit)
from PyQt6.QtCore import Qt, QSize, QDateTime
from PyQt6.QtGui import QPixmap, QFont, QIcon

from core.language_manager import tr, _current_language

class InputDialog(QDialog):
    """Generic input dialog"""
    
    def __init__(self, title, prompt, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle(title)
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        
        # Add prompt label
        label = QLabel(prompt)
        # Set text alignment based on language
        if _current_language == "ar":
            label.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(label)
        
        # Add input field
        self.input_field = QLineEdit()
        # Set text direction based on language
        if _current_language == "ar":
            self.input_field.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        layout.addWidget(self.input_field)
        
        # Add buttons with translated text
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        if _current_language == "ar":
            button_box.button(QDialogButtonBox.StandardButton.Ok).setText(tr("OK"))
            button_box.button(QDialogButtonBox.StandardButton.Cancel).setText(tr("Cancel"))
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def get_input(self):
        """Get the entered text"""
        return self.input_field.text()

class AddPlaylistDialog(QDialog):
    """Dialog for adding a new playlist"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle(tr("Add New Playlist"))
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        
        # Playlist name input
        name_layout = QHBoxLayout()
        name_label = QLabel(tr("Name:"))
        name_layout.addWidget(name_label)
        self.name_input = QLineEdit()
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        if _current_language == "ar":
            button_box.button(QDialogButtonBox.StandardButton.Ok).setText(tr("OK"))
            button_box.button(QDialogButtonBox.StandardButton.Cancel).setText(tr("Cancel"))
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def get_playlist_name(self):
        """Get the entered playlist name"""
        return self.name_input.text()

class AboutDialog(QDialog):
    """مربع حوار لعرض معلومات حول البرنامج/المطور/التحديثات"""
    
    def __init__(self, title="", content="", parent=None):
        super().__init__(parent)
        
        self.setWindowTitle(title)
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        
        # إنشاء تخطيط عمودي
        layout = QVBoxLayout(self)
        
        # إضافة شعار (اختياري)
        try:
            logo_label = QLabel()
            pixmap = QPixmap("resources/icons/logo.png")
            if not pixmap.isNull():
                logo_label.setPixmap(pixmap.scaledToWidth(100, Qt.TransformationMode.SmoothTransformation))
                logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                layout.addWidget(logo_label)
        except Exception:
            pass  # تجاهل إذا لم يكن هناك شعار
        
        # إضافة محتوى النص مع تنسيق أفضل
        content_browser = QTextBrowser()
        
        # Set text direction based on language
        if _current_language == "ar":
            dir_style = "rtl"
            align_style = "right"
        else:
            dir_style = "ltr"
            align_style = "left"
            
        content_browser.setHtml(f"<div style='direction: {dir_style}; text-align: {align_style}; font-family: Arial; font-size: 12pt;'>{content.replace('\n', '<br>')}</div>")
        content_browser.setOpenExternalLinks(True)
        layout.addWidget(content_browser)
        
        # إضافة أزرار
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        button_box.accepted.connect(self.accept)
        layout.addWidget(button_box)

class PlaylistManagerDialog(QDialog):
    """Dialog for managing playlists"""
    
    def __init__(self, playlist_manager, parent=None):
        super().__init__(parent)
        
        self.playlist_manager = playlist_manager
        self.changes_made = False
        
        self.setWindowTitle(tr("Playlist Manager"))
        self.resize(800, 500)
        
        # Create layout
        layout = QVBoxLayout(self)
        
        # Create tab widget
        tab_widget = QTabWidget()
        
        # Create tabs
        self._create_playlists_tab(tab_widget)
        self._create_history_tab(tab_widget)
        
        layout.addWidget(tab_widget)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def _create_playlists_tab(self, tab_widget):
        """Create the playlists management tab"""
        playlists_tab = QWidget()
        layout = QVBoxLayout(playlists_tab)
        
        # Create top action buttons
        actions_layout = QHBoxLayout()
        
        new_btn = QPushButton(tr("New Playlist"))
        new_btn.clicked.connect(self._create_new_playlist)
        actions_layout.addWidget(new_btn)
        
        rename_btn = QPushButton(tr("Rename"))
        rename_btn.clicked.connect(self._rename_selected_playlist)
        actions_layout.addWidget(rename_btn)
        
        delete_btn = QPushButton(tr("Delete"))
        delete_btn.clicked.connect(self._delete_selected_playlist)
        actions_layout.addWidget(delete_btn)
        
        actions_layout.addStretch()
        
        layout.addLayout(actions_layout)
        
        # Create list of playlists
        self.playlists_list = QListWidget()
        layout.addWidget(self.playlists_list)
        
        # Populate the list
        self._populate_playlists_list()
        
        tab_widget.addTab(playlists_tab, tr("Playlists"))
    
    def _create_history_tab(self, tab_widget):
        """Create the history tab"""
        history_tab = QWidget()
        layout = QVBoxLayout(history_tab)
        
        # Create list widget for history
        self.history_list = QListWidget()
        layout.addWidget(self.history_list)
        
        # Populate history
        self._populate_history_list()
        
        tab_widget.addTab(history_tab, tr("History"))
    
    def _populate_playlists_list(self):
        """Populate the playlists list"""
        self.playlists_list.clear()
        
        for name, playlist in self.playlist_manager.playlists.items():
            item = QListWidgetItem(name)
            item.setData(Qt.ItemDataRole.UserRole, name)
            item.setToolTip(f"{tr('Channels')}: {len(playlist.channels)}")
            self.playlists_list.addItem(item)
    
    def _populate_history_list(self):
        """Populate the history list"""
        self.history_list.clear()
        
        history = self.playlist_manager.get_playlist_history()
        for entry in history:
            # Format dates for display
            created_dt = QDateTime.fromString(entry['created'].split('.')[0], "yyyy-MM-ddThh:mm:ss")
            updated_dt = QDateTime.fromString(entry['last_updated'].split('.')[0], "yyyy-MM-ddThh:mm:ss")
            
            created = created_dt.toString("yyyy-MM-dd hh:mm:ss")
            updated = updated_dt.toString("yyyy-MM-dd hh:mm:ss")
            
            # Create item
            item_text = f"{entry['name']} ({tr('Channels')}: {entry['channel_count']})"
            item = QListWidgetItem(item_text)
            
            # Add tooltip with details
            tooltip = f"{tr('Name')}: {entry['name']}\n"
            tooltip += f"{tr('Channels')}: {entry['channel_count']}\n"
            tooltip += f"{tr('Created')}: {created}\n"
            tooltip += f"{tr('Last Updated')}: {updated}"
            item.setToolTip(tooltip)
            
            self.history_list.addItem(item)
    
    def _create_new_playlist(self):
        """Create a new playlist"""
        name, ok = QInputDialog.getText(
            self, 
            tr("New Playlist"), 
            tr("Enter playlist name:")
        )
        
        if ok and name:
            if name in self.playlist_manager.playlists:
                QMessageBox.warning(
                    self,
                    tr("Duplicate Name"),
                    tr("A playlist with this name already exists.")
                )
                return
                
            self.playlist_manager.create_playlist(name)
            self._populate_playlists_list()
            self._populate_history_list()
            self.changes_made = True
    
    def _rename_selected_playlist(self):
        """Rename the selected playlist"""
        selected_items = self.playlists_list.selectedItems()
        if not selected_items:
            return
            
        old_name = selected_items[0].data(Qt.ItemDataRole.UserRole)
        
        new_name, ok = QInputDialog.getText(
            self, 
            tr("Rename Playlist"), 
            tr("Enter new name:"),
            text=old_name
        )
        
        if ok and new_name and new_name != old_name:
            if new_name in self.playlist_manager.playlists:
                QMessageBox.warning(
                    self,
                    tr("Duplicate Name"),
                    tr("A playlist with this name already exists.")
                )
                return
                
            if self.playlist_manager.rename_playlist(old_name, new_name):
                self._populate_playlists_list()
                self._populate_history_list()
                self.changes_made = True
    
    def _delete_selected_playlist(self):
        """Delete the selected playlist"""
        selected_items = self.playlists_list.selectedItems()
        if not selected_items:
            return
            
        playlist_name = selected_items[0].data(Qt.ItemDataRole.UserRole)
        
        confirm = QMessageBox.question(
            self,
            tr("Confirm Delete"),
            tr("Are you sure you want to delete playlist '{name}'?").format(name=playlist_name),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if confirm == QMessageBox.StandardButton.Yes:
            if self.playlist_manager.delete_playlist(playlist_name):
                self._populate_playlists_list()
                self._populate_history_list()
                self.changes_made = True
    
    def accept(self) -> None:
        """Override accept to return whether changes were made"""
        self.done(int(self.changes_made))
    
    def reject(self) -> None:
        """Override reject to return whether changes were made"""
        self.done(int(self.changes_made))

class AddToPlaylistDialog(QDialog):
    """Dialog for adding a channel to a playlist"""
    
    def __init__(self, playlist_manager, channel, parent=None):
        super().__init__(parent)
        
        self.playlist_manager = playlist_manager
        self.channel = channel
        self.selected_playlist = None
        
        self.setWindowTitle(tr("Add to Playlist"))
        self.resize(400, 300)
        
        # Create layout
        layout = QVBoxLayout(self)
        
        # Channel info
        if _current_language == "ar":
            layout.addWidget(QLabel(f"<b>{tr('Channel')}:</b> {channel.name}"))
        else:
            layout.addWidget(QLabel(f"<b>{tr('Channel')}:</b> {channel.name}"))
        
        # Playlist selection list
        layout.addWidget(QLabel(tr("Select playlist:")))
        
        self.playlist_list = QListWidget()
        layout.addWidget(self.playlist_list)
        
        # Populate the list
        self._populate_playlist_list()
        
        # New playlist button
        new_playlist_btn = QPushButton(tr("Create New Playlist"))
        new_playlist_btn.clicked.connect(self._create_new_playlist)
        layout.addWidget(new_playlist_btn)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self._on_accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        # Set OK button as disabled until a playlist is selected
        self.ok_button = button_box.button(QDialogButtonBox.StandardButton.Ok)
        self.ok_button.setEnabled(False)
        
        self.playlist_list.itemSelectionChanged.connect(self._on_selection_changed)
    
    def _populate_playlist_list(self):
        """Populate the playlist list"""
        self.playlist_list.clear()
        
        for name in self.playlist_manager.playlists:
            item = QListWidgetItem(name)
            item.setData(Qt.ItemDataRole.UserRole, name)
            self.playlist_list.addItem(item)
    
    def _on_selection_changed(self):
        """Handle selection change"""
        self.ok_button.setEnabled(len(self.playlist_list.selectedItems()) > 0)
    
    def _create_new_playlist(self):
        """Create a new playlist"""
        name, ok = QInputDialog.getText(
            self, 
            tr("New Playlist"), 
            tr("Enter playlist name:")
        )
        
        if ok and name:
            if name in self.playlist_manager.playlists:
                QMessageBox.warning(
                    self,
                    tr("Duplicate Name"),
                    tr("A playlist with this name already exists.")
                )
                return
                
            self.playlist_manager.create_playlist(name)
            self._populate_playlist_list()
            
            # Select the new playlist
            for i in range(self.playlist_list.count()):
                item = self.playlist_list.item(i)
                if item.data(Qt.ItemDataRole.UserRole) == name:
                    self.playlist_list.setCurrentItem(item)
                    break
    
    def _on_accept(self):
        """Handle OK button click"""
        selected_items = self.playlist_list.selectedItems()
        if not selected_items:
            return
            
        self.selected_playlist = selected_items[0].data(Qt.ItemDataRole.UserRole)
        self.accept()
    
    def get_selected_playlist(self):
        """Return the selected playlist"""
        return self.selected_playlist

class URLInputDialog(QDialog):
    """حوار إدخال رابط مع عرض سجل الروابط السابقة"""
    
    def __init__(self, history_urls, title, prompt, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle(title)
        self.setMinimumWidth(500)
        self.setMinimumHeight(300)
        
        layout = QVBoxLayout(self)
        
        # Add prompt label
        label = QLabel(prompt)
        # Set text alignment based on language
        if _current_language == "ar":
            label.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(label)
        
        # Add input field
        self.input_field = QLineEdit()
        # Set text direction based on language
        if _current_language == "ar":
            self.input_field.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        layout.addWidget(self.input_field)
        
        # إضافة تسمية للسجل
        history_label = QLabel(tr("Recent URLs:"))
        if _current_language == "ar":
            history_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(history_label)
        
        # إضافة قائمة الروابط السابقة
        self.history_list = QListWidget()
        for url in history_urls:
            item = QListWidgetItem(url)
            self.history_list.addItem(item)
        
        # عند النقر على عنصر في السجل، يتم نسخه إلى حقل الإدخال
        self.history_list.itemClicked.connect(self._url_selected)
        
        layout.addWidget(self.history_list)
        
        # Add buttons with translated text
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        if _current_language == "ar":
            button_box.button(QDialogButtonBox.StandardButton.Ok).setText(tr("OK"))
            button_box.button(QDialogButtonBox.StandardButton.Cancel).setText(tr("Cancel"))
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def get_input(self):
        """Get the entered text"""
        return self.input_field.text()
    
    def _url_selected(self, item):
        """Handler for when a URL is selected from history"""
        self.input_field.setText(item.text())

class ContactDialog(QDialog):
    """Dialog for contacting the developers"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle(tr("Contact Us"))
        self.setMinimumWidth(500)
        self.setMinimumHeight(350)
        
        layout = QVBoxLayout(self)
        
        # Add logo if available
        try:
            logo_label = QLabel()
            pixmap = QPixmap("resources/icons/logo.png")
            if not pixmap.isNull():
                logo_label.setPixmap(pixmap.scaledToWidth(100, Qt.TransformationMode.SmoothTransformation))
                logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                layout.addWidget(logo_label)
        except Exception:
            pass  # Ignore if logo not available
        
        # Add title
        title_label = QLabel(tr("Get In Touch"))
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Add contact information in tabs
        tabs = QTabWidget()
        layout.addWidget(tabs)
        
        # Support tab
        support_tab = QWidget()
        support_layout = QVBoxLayout(support_tab)
        
        support_info = QTextBrowser()
        # Set text direction based on language
        if _current_language == "ar":
            dir_style = "rtl"
            align_style = "right"
        else:
            dir_style = "ltr"
            align_style = "left"
        
        support_content = tr("""
        <h3>Technical Support</h3>
        <p>If you have technical issues or questions about the application, please contact us:</p>
        <ul>
            <li><b>Email:</b> admin@aljup.com</li>
        </ul>
        <p>Please include detailed information about your issue and your system configuration.</p>
        """)
        
        support_info.setHtml(f"<div style='direction: {dir_style}; text-align: {align_style}; font-family: Arial; font-size: 12pt;'>{support_content}</div>")
        support_info.setOpenExternalLinks(True)
        support_layout.addWidget(support_info)
        tabs.addTab(support_tab, tr("Support"))
        
        # Feedback tab
        feedback_tab = QWidget()
        feedback_layout = QVBoxLayout(feedback_tab)
        
        feedback_label = QLabel(tr("We value your feedback! Please share your thoughts, suggestions, or report any issues:"))
        feedback_layout.addWidget(feedback_label)
        
        # Add a simple feedback form
        name_layout = QHBoxLayout()
        name_label = QLabel(tr("Name:"))
        name_layout.addWidget(name_label)
        self.name_input = QLineEdit()
        name_layout.addWidget(self.name_input)
        feedback_layout.addLayout(name_layout)
        
        email_layout = QHBoxLayout()
        email_label = QLabel(tr("Email:"))
        email_layout.addWidget(email_label)
        self.email_input = QLineEdit()
        email_layout.addWidget(self.email_input)
        feedback_layout.addLayout(email_layout)
        
        message_label = QLabel(tr("Message:"))
        feedback_layout.addWidget(message_label)
        
        self.message_text = QTextEdit()
        feedback_layout.addWidget(self.message_text)
        
        submit_button = QPushButton(tr("Submit"))
        submit_button.clicked.connect(self.submit_feedback)
        feedback_layout.addWidget(submit_button)
        
        tabs.addTab(feedback_tab, tr("Feedback"))
        
        # Social Media tab
        social_tab = QWidget()
        social_layout = QVBoxLayout(social_tab)
        
        social_info = QTextBrowser()
        social_content = tr("""
        <h3>Follow Us</h3>
        <p>Stay updated with the latest news and updates:</p>
        <ul>
            <li><b>Website:</b> <a href="https://www.aljup.com">www.aljup.com</a></li>
            <li><b>Whatsapp:</b> <a href="https://wa.me/967738977414">+967738977414</a></li>
            <li><b>GitHub:</b> <a href="https://github.com/myaga2025/Modern-IPTV-Player">@Modern-IPTV-Player</a></li>
        </ul>
        """)
        
        social_info.setHtml(f"<div style='direction: {dir_style}; text-align: {align_style}; font-family: Arial; font-size: 12pt;'>{social_content}</div>")
        social_info.setOpenExternalLinks(True)
        social_layout.addWidget(social_info)
        tabs.addTab(social_tab, tr("Social Media"))
        
        # Add close button
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def submit_feedback(self):
        """Handle feedback submission"""
        name = self.name_input.text()
        email = self.email_input.text()
        message = self.message_text.toPlainText()
        
        if not name or not email or not message:
            QMessageBox.warning(self, tr("Incomplete Form"), tr("Please fill in all fields."))
            return
        
        # Here you would typically send the feedback to a server
        # For now, we'll just show a success message
        QMessageBox.information(
            self,
            tr("Feedback Submitted"),
            tr("Thank you for your feedback! We will review it soon.")
        )
        self.accept()
