import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
                             QHeaderView, QAbstractItemView, QMenu)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QColor, QBrush

class PlaylistWidget(QWidget):
    """Widget for displaying and managing playlists"""
    
    channel_selected = pyqtSignal(object)
    
    def __init__(self):
        super().__init__()
        
        self.channels = []
        self.filtered_channels = []
        self.active_channel_row = -1  # Track the currently active channel row
        self.active_channel_id = None  # Track the currently active channel ID
        
        # Setup UI
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup the widget UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create table for channels
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["", "Channel", "Category"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.setColumnWidth(0, 40)  # Logo column
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)  # Better visual indication of rows
        
        # Connect signals
        self.table.cellDoubleClicked.connect(self._on_channel_double_clicked)
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._show_context_menu)
        
        layout.addWidget(self.table)
    
    def set_channels(self, channels):
        """Set channels to display in the widget"""
        print(f"Setting {len(channels)} channels in playlist widget")
        self.channels = channels
        self.filtered_channels = channels
        self._refresh_table()
    
    def set_active_channel(self, channel_id):
        """Mark a channel as currently active/playing"""
        print(f"Setting active channel ID: {channel_id}")
        
        # Reset previous active channel styling
        if self.active_channel_row >= 0 and self.active_channel_row < self.table.rowCount():
            for col in range(self.table.columnCount()):
                item = self.table.item(self.active_channel_row, col)
                if item:
                    # Use Qt.ItemDataRole.UserRole + 1 for active status
                    item.setData(Qt.ItemDataRole.UserRole + 1, False)
                    # Force property update using dynamic property
                    item.setData(Qt.ItemDataRole.AccessibleTextRole, "false")
        
        # Update active channel ID
        self.active_channel_id = channel_id
        self.active_channel_row = -1
        
        # Find and mark the new active channel
        for row in range(self.table.rowCount()):
            name_item = self.table.item(row, 1)  # Channel name column
            if name_item:
                channel_data = name_item.data(Qt.ItemDataRole.UserRole)
                if channel_data and channel_data.get('id') == channel_id:
                    self.active_channel_row = row
                    
                    # Mark all cells in this row as active
                    for col in range(self.table.columnCount()):
                        item = self.table.item(row, col)
                        if item:
                            # Set both UserRole+1 and dynamic property
                            item.setData(Qt.ItemDataRole.UserRole + 1, True)
                            item.setData(Qt.ItemDataRole.AccessibleTextRole, "true")
                    break
        
        print(f"Active channel row set to: {self.active_channel_row}")
        
        # Force visual update - very important!
        self.table.viewport().update()
    
    def _refresh_table(self):
        """Refresh the table with current channels"""
        # Clear current items
        self.table.clearContents()
        self.table.setRowCount(0)
        
        if not self.filtered_channels:
            print("No channels to display")
            return
        
        print(f"Refreshing table with {len(self.filtered_channels)} channels")
        
        # Pre-set row count for better performance
        self.table.setRowCount(len(self.filtered_channels))
        
        # Track if we found the active channel
        found_active_channel = False
        
        # Add channels to table
        for i, channel in enumerate(self.filtered_channels):
            # Check if this is the active channel
            is_active = self.active_channel_id is not None and channel.get('id') == self.active_channel_id
            if is_active:
                found_active_channel = True
                self.active_channel_row = i
                print(f"Found active channel at row {i}: {channel.get('name')}")
            
            # Logo item (column 0)
            logo_item = QTableWidgetItem()
            if 'logo' in channel and channel['logo']:
                try:
                    logo_icon = QIcon(channel['logo'])
                    logo_item.setIcon(logo_icon)
                except Exception as e:
                    print(f"Error loading logo for channel {channel.get('name')}: {e}")
                    default_icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                                "resources", "icons", "tv_icon.png")
                    if os.path.exists(default_icon_path):
                        logo_item.setIcon(QIcon(default_icon_path))
            
            # Add the active property for CSS styling
            logo_item.setData(Qt.ItemDataRole.UserRole + 1, is_active)
            logo_item.setData(Qt.ItemDataRole.AccessibleTextRole, "true" if is_active else "false")
            self.table.setItem(i, 0, logo_item)
            
            # Name item (column 1)
            name = channel.get('name', f"Channel {i+1}")
            name_item = QTableWidgetItem(name)
            channel_copy = channel.copy()
            name_item.setData(Qt.ItemDataRole.UserRole, channel_copy)
            name_item.setData(Qt.ItemDataRole.UserRole + 1, is_active)
            name_item.setData(Qt.ItemDataRole.AccessibleTextRole, "true" if is_active else "false")
            self.table.setItem(i, 1, name_item)
            
            # Group item (column 2)
            group = channel.get('group', 'Unknown')
            group_item = QTableWidgetItem(group)
            group_item.setData(Qt.ItemDataRole.UserRole + 1, is_active)
            group_item.setData(Qt.ItemDataRole.AccessibleTextRole, "true" if is_active else "false")
            self.table.setItem(i, 2, group_item)
        
        # Force a visual update
        self.table.resizeRowsToContents()
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.viewport().update()
        
        # If active channel wasn't found in the filtered list, reset tracking
        if not found_active_channel:
            self.active_channel_row = -1
        
        print(f"Table refresh complete with {self.table.rowCount()} rows, active row: {self.active_channel_row}")
    
    def _on_channel_double_clicked(self, row, column):
        """Handle double-click on channel row"""
        if row < 0 or row >= self.table.rowCount():
            print(f"Invalid row index: {row}")
            return
            
        channel_item = self.table.item(row, 1)  # Name column
        if not channel_item:
            print(f"No item found at row {row}, column 1")
            return
            
        channel_data = channel_item.data(Qt.ItemDataRole.UserRole)
        if not channel_data:
            print(f"No channel data found for row {row}")
            return
        
        # Create a channel-like object from the dictionary
        class Channel:
            pass
        
        channel = Channel()
        for key, value in channel_data.items():
            setattr(channel, key, value)
        
        # Emit signal - the main window will handle setting the active channel
        print(f"Emitting channel selected signal for: {channel.name}")
        self.channel_selected.emit(channel)
    
    def _show_context_menu(self, position):
        """Show context menu for channel"""
        row = self.table.rowAt(position.y())
        if row < 0:
            return
            
        menu = QMenu(self)
        play_action = menu.addAction("Play")
        add_to_playlist_action = menu.addAction("Add to Playlist")
        
        action = menu.exec(self.table.mapToGlobal(position))
        if action == play_action:
            self._on_channel_double_clicked(row, 1)
    
    def search(self, query):
        """Search channels by name"""
        if not query:
            self.filtered_channels = self.channels
        else:
            query = query.lower()
            self.filtered_channels = [
                channel for channel in self.channels 
                if query in channel.get('name', '').lower()
            ]
        
        print(f"Search for '{query}' returned {len(self.filtered_channels)} results")
        self._refresh_table()
