"""
Telegram Forwarder
Developed by Zack Whitson
Telegram: @definitezer0
X (Twitter): @Delirium_Pulse
Website: www.zackwhitson.com
Upwork: https://www.upwork.com/freelancers/~01b74427823660e746
"""
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QComboBox, QListWidget, QListWidgetItem, QTextEdit, QGroupBox, QTabWidget, QMessageBox,
    QCheckBox
)
from PyQt6.QtCore import Qt, pyqtSlot, QTimer
from client_manager import ClientManager
import config
import asyncio
import json
import os

class MainWindow(QWidget):
    def __init__(self, client_manager: ClientManager):
        super().__init__()
        self.client_manager = client_manager
        self.setWindowTitle("Telegram Forwarder")
        self.resize(600, 700)
        
        self.init_ui()
        self.connect_signals()
        self.load_saved_config()
        self.selected_destinations = set()
        # Initialize from saved targets if available
        if hasattr(self, 'saved_targets'):
            self.selected_destinations = set(map(str, self.saved_targets.get('destination_ids', [])))
            if not self.selected_destinations:
                self.selected_destinations.add('me') # Default

        # Auto-Login Attempt (Deferred to ensure event loop is running)
        QTimer.singleShot(0, self.attempt_auto_login)

    def attempt_auto_login(self):
        cfg = config.load_config()
        api_id = cfg.get("api_id")
        api_hash = cfg.get("api_hash")
        phone = cfg.get("phone")
        
        if not api_id or not api_hash or not phone:
            return

        # Check if session file exists
        # ClientManager uses 'session_{phone}' naming convention
        session_name = f"session_{phone}.session"
        session_exists = os.path.exists(session_name)
        
        if session_exists:
            self.append_log(f"Found saved session ({session_name}). Auto-connecting...")
            self.login_btn.setEnabled(False)
            asyncio.create_task(self.client_manager.connect_client(int(api_id), api_hash, phone))
        else:
            self.append_log("No saved session found. Please login.")

    def init_ui(self):
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # Tabs
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # Login Tab
        self.login_tab = QWidget()
        self.setup_login_tab()
        self.tabs.addTab(self.login_tab, "Login")

        # Dashboard Tab
        self.dashboard_tab = QWidget()
        self.setup_dashboard_tab()
        self.tabs.addTab(self.dashboard_tab, "Dashboard")
        self.tabs.setTabEnabled(1, False) # Disable dashboard until logged in

    def setup_login_tab(self):
        layout = QVBoxLayout()
        self.login_tab.setLayout(layout)

        # Credentials Group
        creds_group = QGroupBox("API Credentials")
        creds_layout = QVBoxLayout()
        
        self.api_id_input = QLineEdit()
        self.api_id_input.setPlaceholderText("API ID")
        creds_layout.addWidget(QLabel("API ID:"))
        creds_layout.addWidget(self.api_id_input)

        self.api_hash_input = QLineEdit()
        self.api_hash_input.setPlaceholderText("API Hash")
        creds_layout.addWidget(QLabel("API Hash:"))
        creds_layout.addWidget(self.api_hash_input)

        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("Phone Number (e.g., +1234567890)")
        creds_layout.addWidget(QLabel("Phone Number:"))
        creds_layout.addWidget(self.phone_input)

        self.login_btn = QPushButton("Login (Send Code)")
        self.login_btn.clicked.connect(self.on_login_clicked)
        creds_layout.addWidget(self.login_btn)

        creds_group.setLayout(creds_layout)
        layout.addWidget(creds_group)

        # Verification Group
        verify_group = QGroupBox("Verification")
        verify_layout = QVBoxLayout()

        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("Verification Code")
        verify_layout.addWidget(QLabel("Code:"))
        verify_layout.addWidget(self.code_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("2FA Password (Optional)")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        verify_layout.addWidget(QLabel("Password:"))
        verify_layout.addWidget(self.password_input)

        self.verify_btn = QPushButton("Verify & Sign In")
        self.verify_btn.clicked.connect(self.on_verify_clicked)
        self.verify_btn.setEnabled(False)
        verify_layout.addWidget(self.verify_btn)

        verify_group.setLayout(verify_layout)
        layout.addWidget(verify_group)
        
        layout.addStretch()

    def setup_dashboard_tab(self):
        layout = QVBoxLayout()
        self.dashboard_tab.setLayout(layout)

        # Selection Area
        selection_group = QGroupBox("Target Selection")
        selection_layout = QVBoxLayout()

        # Search Bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search groups...")
        self.search_input.textChanged.connect(self.filter_groups)
        selection_layout.addWidget(self.search_input)

        group_layout = QHBoxLayout()
        self.group_combo = QComboBox()
        self.group_combo.currentIndexChanged.connect(self.on_group_selected)
        self.refresh_btn = QPushButton("Refresh Groups")
        self.refresh_btn.clicked.connect(self.on_refresh_groups)
        group_layout.addWidget(self.group_combo)
        group_layout.addWidget(self.refresh_btn)
        selection_layout.addLayout(group_layout)

        selection_layout.addWidget(QLabel("Select Members to Monitor:"))
        
        self.monitor_all_chk = QCheckBox("Monitor All Messages (Ignore Member List)")
        self.monitor_all_chk.stateChanged.connect(self.on_monitor_all_changed)
        selection_layout.addWidget(self.monitor_all_chk)

        self.member_list = QListWidget()
        selection_layout.addWidget(self.member_list)

        selection_group.setLayout(selection_layout)
        layout.addWidget(selection_group)

        # Destination Area
        dest_group = QGroupBox("Destination Selection")
        dest_layout = QVBoxLayout()
        dest_layout.addWidget(QLabel("Select where to forward messages:"))
        
        self.dest_search_input = QLineEdit()
        self.dest_search_input.setPlaceholderText("🔍 Search destinations...")
        self.dest_search_input.textChanged.connect(self.filter_destinations)
        dest_layout.addWidget(self.dest_search_input)

        self.dest_list = QListWidget()
        self.dest_list.itemChanged.connect(self.on_dest_item_changed)
        dest_layout.addWidget(self.dest_list)
        
        dest_group.setLayout(dest_layout)
        layout.addWidget(dest_group)

        # Control Area
        control_layout = QHBoxLayout()
        self.start_btn = QPushButton("Start Monitor")
        self.start_btn.clicked.connect(self.on_start_monitor)
        
        self.stop_btn = QPushButton("Stop Monitor")
        self.stop_btn.clicked.connect(self.on_stop_monitor)
        self.stop_btn.setEnabled(False)

        self.clear_btn = QPushButton("Clear Selection")
        self.clear_btn.clicked.connect(self.on_clear_selection)

        control_layout.addWidget(self.start_btn)
        control_layout.addWidget(self.stop_btn)
        control_layout.addWidget(self.clear_btn)
        
        layout.addLayout(control_layout)

        # Log Console
        self.log_console = QTextEdit()
        self.log_console.setReadOnly(True)
        layout.addWidget(self.log_console)

        self.dashboard_tab.setLayout(layout)
        
        # Load saved targets
        self.saved_targets = {}
        try:
            if os.path.exists("targets.json"):
                with open("targets.json", "r") as f:
                    self.saved_targets = json.load(f)
        except Exception as e:
            print(f"Error loading targets: {e}")

    def connect_signals(self):
        self.client_manager.log_signal.connect(self.append_log)
        self.client_manager.connection_status_signal.connect(self.on_connection_status)
        self.client_manager.code_requested_signal.connect(self.on_code_requested)
        self.client_manager.login_success_signal.connect(self.on_login_success)
        self.client_manager.login_failed_signal.connect(self.on_login_failed)

    def load_saved_config(self):
        cfg = config.load_config()
        if cfg:
            self.api_id_input.setText(cfg.get("api_id", ""))
            self.api_hash_input.setText(cfg.get("api_hash", ""))
            self.phone_input.setText(cfg.get("phone", ""))

    @pyqtSlot(str)
    def append_log(self, message):
        self.log_console.append(message)

    @pyqtSlot()
    def on_login_clicked(self):
        api_id = self.api_id_input.text().strip()
        api_hash = self.api_hash_input.text().strip()
        phone = self.phone_input.text().strip()

        if not api_id or not api_hash or not phone:
            QMessageBox.warning(self, "Error", "Please fill in all credentials.")
            return

        # Save config
        config.save_config(api_id, api_hash, phone)
        
        self.login_btn.setEnabled(False)
        self.append_log("Connecting...")
        
        # Start async connection
        asyncio.create_task(self.client_manager.connect_client(int(api_id), api_hash, phone))

    @pyqtSlot()
    def on_code_requested(self):
        self.append_log("Code requested. Please check your Telegram app.")
        self.verify_btn.setEnabled(True)
        self.code_input.setFocus()

    @pyqtSlot()
    def on_verify_clicked(self):
        code = self.code_input.text().strip()
        password = self.password_input.text().strip()
        
        if not code:
            QMessageBox.warning(self, "Error", "Please enter the verification code.")
            return
            
        self.verify_btn.setEnabled(False)
        asyncio.create_task(self.client_manager.complete_login(code, password))

    @pyqtSlot()
    def on_login_success(self):
        self.tabs.setTabEnabled(1, True)
        self.tabs.setCurrentIndex(1)
        self.append_log("Login successful! You can now select groups.")
        self.on_refresh_groups()

    @pyqtSlot(str)
    def on_login_failed(self, error):
        self.login_btn.setEnabled(True)
        self.verify_btn.setEnabled(True)
        QMessageBox.critical(self, "Login Failed", error)

    @pyqtSlot(bool)
    def on_connection_status(self, connected):
        if connected:
            self.login_btn.setText("Connected")
            self.login_btn.setEnabled(False)

    @pyqtSlot()
    def on_refresh_groups(self):
        self.refresh_btn.setEnabled(False)
        asyncio.create_task(self.fetch_groups())

    async def fetch_groups(self):
        self.append_log("Fetching groups...")
        dialogs = await self.client_manager.get_dialogs()
        
        # Store all dialogs for filtering
        self.all_dialogs = dialogs
        
        self.group_combo.clear()
        for dialog_id, name in dialogs:
            self.group_combo.addItem(name, dialog_id)
        self.refresh_btn.setEnabled(True)
        self.append_log(f"Fetched {len(dialogs)} groups.")
        
        # Populate destinations
        self.update_dest_list()

    def update_dest_list(self, filter_text=""):
        self.dest_list.clear()
        filter_text = filter_text.lower()
        
        # Always add Saved Messages if it matches or filter is empty
        if not filter_text or "saved messages" in filter_text:
            saved_item = QListWidgetItem("Saved Messages")
            saved_item.setData(Qt.ItemDataRole.UserRole, 'me')
            saved_item.setFlags(saved_item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            
            if 'me' in self.selected_destinations:
                 saved_item.setCheckState(Qt.CheckState.Checked)
            else:
                 saved_item.setCheckState(Qt.CheckState.Unchecked)
            self.dest_list.addItem(saved_item)

        if hasattr(self, 'all_dialogs'):
            for dialog_id, name in self.all_dialogs:
                if filter_text and filter_text not in name.lower():
                    continue
                    
                item = QListWidgetItem(name)
                item.setData(Qt.ItemDataRole.UserRole, dialog_id)
                item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                
                if str(dialog_id) in self.selected_destinations:
                     item.setCheckState(Qt.CheckState.Checked)
                else:
                     item.setCheckState(Qt.CheckState.Unchecked)
                
                self.dest_list.addItem(item)
        
        # Connect signal after populating to avoid triggering during population
        # Actually, itemChanged is emitted when user clicks.
        # We need to be careful not to trigger it when we setCheckState programmatically?
        # QListWidget.itemChanged is emitted when the item's data changes.
        # We can block signals or handle it carefully.
        # Let's connect once in init/setup and handle the source of change if possible,
        # or just update self.selected_destinations whenever it changes.
        
    @pyqtSlot(QListWidgetItem)
    def on_dest_item_changed(self, item):
        dest_id = str(item.data(Qt.ItemDataRole.UserRole))
        if item.checkState() == Qt.CheckState.Checked:
            self.selected_destinations.add(dest_id)
        else:
            self.selected_destinations.discard(dest_id)

    @pyqtSlot(str)
    def filter_destinations(self, text):
        self.dest_list.blockSignals(True)
        self.update_dest_list(text)
        self.dest_list.blockSignals(False)
        
    @pyqtSlot(str)
    def filter_groups(self, text):
        text = text.lower()
        self.group_combo.blockSignals(True)
        self.group_combo.clear()
        
        if hasattr(self, 'all_dialogs'):
            for dialog_id, name in self.all_dialogs:
                if text in name.lower():
                    self.group_combo.addItem(name, dialog_id)
        
        self.group_combo.blockSignals(False)
        # Trigger selection update if items exist
        if self.group_combo.count() > 0:
            self.on_group_selected(0)

    @pyqtSlot(int)
    def on_group_selected(self, index):
        group_id = self.group_combo.currentData()
        if group_id:
            # Restore state from existing config if available
            source_id = str(group_id)
            if source_id in self.client_manager.sources:
                config = self.client_manager.sources[source_id]
                self.monitor_all_chk.setChecked(config.get('monitor_all', False))
                self.append_log(f"Restored settings for {config.get('name')}")
            else:
                self.monitor_all_chk.setChecked(False)
            
            asyncio.create_task(self.fetch_members(group_id))

    async def fetch_members(self, group_id):
        self.member_list.clear()
        self.append_log(f"Fetching members for group ID {group_id}...")
        participants = await self.client_manager.get_participants(group_id)
        
        # Get saved user IDs for this group
        source_id = str(group_id)
        saved_users = set()
        if source_id in self.client_manager.sources:
            saved_users = set(self.client_manager.sources[source_id].get('user_ids', []))

        for user_id, name, username in participants:
            display_text = f"{name} (@{username})" if username else name
            item = QListWidgetItem(display_text)
            item.setData(Qt.ItemDataRole.UserRole, user_id)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            
            if user_id in saved_users:
                item.setCheckState(Qt.CheckState.Checked)
            else:
                item.setCheckState(Qt.CheckState.Unchecked)
                
            self.member_list.addItem(item)
        
        # Connect item changed signal to update config
        self.member_list.itemChanged.connect(self.update_source_config)
        
        self.append_log(f"Fetched {len(participants)} members.")

    @pyqtSlot()
    def on_monitor_all_changed(self):
        is_checked = self.monitor_all_chk.isChecked()
        self.member_list.setEnabled(not is_checked)
        self.update_source_config()

    def update_source_config(self):
        group_id = self.group_combo.currentData()
        if not group_id: return

        source_id = str(group_id)
        monitor_all = self.monitor_all_chk.isChecked()
        
        selected_users = []
        if not monitor_all:
            for i in range(self.member_list.count()):
                item = self.member_list.item(i)
                if item.checkState() == Qt.CheckState.Checked:
                    selected_users.append(item.data(Qt.ItemDataRole.UserRole))

        # Logic: If nothing selected and not monitor all, remove from sources
        # If something selected or monitor all, add/update sources
        
        if not monitor_all and not selected_users:
            if source_id in self.client_manager.sources:
                del self.client_manager.sources[source_id]
                self.client_manager.save_targets()
                # self.append_log(f"Removed {source_id} from configuration.")
        else:
            self.client_manager.sources[source_id] = {
                "name": self.group_combo.currentText(),
                "type": "group",
                "monitor_all": monitor_all,
                "user_ids": selected_users
            }
            self.client_manager.save_targets()
            # self.append_log(f"Updated configuration for {self.group_combo.currentText()}.")

    @pyqtSlot()
    def on_start_monitor(self):
        # Save destinations first
        destination_ids = list(self.selected_destinations)
        
        if not destination_ids:
             QMessageBox.warning(self, "Warning", "Please select at least one destination.")
             return

        self.client_manager.destination_ids = destination_ids
        self.client_manager.save_targets()
        
        if not self.client_manager.sources:
             QMessageBox.warning(self, "Warning", "Please configure at least one group (Monitor All or Select Members).")
             return

        self.client_manager.start_monitoring()
        
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.group_combo.setEnabled(False)
        self.member_list.setEnabled(False)
        self.monitor_all_chk.setEnabled(False)
        self.dest_list.setEnabled(False)
        self.search_input.setEnabled(False)

    @pyqtSlot()
    def on_stop_monitor(self):
        self.client_manager.stop_monitoring()
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.group_combo.setEnabled(True)
        self.member_list.setEnabled(not self.monitor_all_chk.isChecked())
        self.monitor_all_chk.setEnabled(True)
        self.dest_list.setEnabled(True)
        self.clear_btn.setEnabled(True)
        self.search_input.setEnabled(True)

    @pyqtSlot()
    def on_clear_selection(self):
        self.group_combo.setCurrentIndex(-1)
        self.member_list.clear()
        self.monitor_all_chk.setChecked(False)
        self.search_input.clear()
        
        # Uncheck all destinations except Saved Messages
        for i in range(self.dest_list.count()):
            item = self.dest_list.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == 'me':
                item.setCheckState(Qt.CheckState.Checked)
            else:
                item.setCheckState(Qt.CheckState.Unchecked)
        
        self.append_log("Selections cleared.")
