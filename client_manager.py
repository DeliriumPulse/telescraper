import asyncio
import json
import os
import random
from telethon import TelegramClient, events, functions
from PyQt6.QtCore import QObject, pyqtSignal

TARGETS_FILE = "targets.json"

class ClientManager(QObject):
    # Signals to update GUI
    log_signal = pyqtSignal(str)
    connection_status_signal = pyqtSignal(bool)
    code_requested_signal = pyqtSignal()
    login_success_signal = pyqtSignal()
    login_failed_signal = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.client = None
        self.phone = None
        self.is_monitoring = False
        
        # Multi-source configuration
        self.sources = {} # {str(id): {'name': str, 'type': str, 'monitor_all': bool, 'user_ids': []}}
        self.destination_ids = ['me'] # Default destination
        self.current_edit_id = None # ID of source currently being edited via commands
        self.message_handlers = [] # List of registered handlers
        
        self.load_targets() # Load persistent settings

    async def connect_client(self, api_id, api_hash, phone):
        self.phone = phone
        try:
            self.client = TelegramClient(f'session_{phone}', api_id, api_hash)
            await self.client.connect()
            
            if not await self.client.is_user_authorized():
                self.log_signal.emit("Client connected. Requesting code...")
                await self.client.send_code_request(phone)
                self.code_requested_signal.emit()
            else:
                self.log_signal.emit("Client already authorized.")
                self.connection_status_signal.emit(True)
                self.login_success_signal.emit()
                
                # If already authorized, ensure command handler is active
                self.register_command_handler()
                
        except Exception as e:
            self.log_signal.emit(f"Connection Error: {str(e)}")
            self.login_failed_signal.emit(str(e))

    async def complete_login(self, code, password=None):
        if not self.client:
            return

        try:
            await self.client.sign_in(self.phone, code, password=password)
            self.log_signal.emit("Login successful!")
            self.connection_status_signal.emit(True)
            self.login_success_signal.emit()
            self.register_command_handler() # Register command handler after successful login
        except Exception as e:
            self.log_signal.emit(f"Login Error: {str(e)}")
            self.login_failed_signal.emit(str(e))

    async def get_dialogs(self, limit=None):
        if not self.client or not await self.client.is_user_authorized():
            return []
        
        dialogs = []
        async for dialog in self.client.iter_dialogs(limit=limit):
            if dialog.is_group or dialog.is_channel:
                dialogs.append((dialog.id, dialog.name))
        return dialogs

    async def get_participants(self, group_id):
        if not self.client:
            return []
        
        participants = []
        try:
            async for user in self.client.iter_participants(group_id):
                if user.deleted:
                    continue
                name = f"{user.first_name or ''} {user.last_name or ''}".strip()
                if not name:
                    name = "Unknown"
                participants.append((user.id, name, user.username))
        except Exception as e:
            # If it's a channel where we can't see participants, just return empty
            if "Chat admin privileges are required" in str(e):
                self.log_signal.emit(f"Note: Cannot fetch members for this channel (Admin required). Use 'Monitor All'.")
            else:
                self.log_signal.emit(f"Error fetching participants: {str(e)}")
            return []
        
        return participants

    def start_monitoring(self, group_id=None, user_ids=None, dest_ids=None, monitor_all=None):
        # Note: Arguments are kept for compatibility but ignored in favor of self.sources for multi-source
        # Ensure previous handlers are removed
        self.stop_monitoring(keep_running=True)
        self.is_monitoring = True
        self.message_handlers = []

        if not self.sources:
            self.log_signal.emit("No sources configured to monitor.")
            return

        for source_id, source_data in self.sources.items():
            try:
                group_id = int(source_id)
                # Telethon sometimes needs the -100 prefix for channels if it wasn't there
                # But usually get_dialogs returns the correct ID with prefix if applicable.
                
                self.log_signal.emit(f"Registering handler for: {source_data.get('name')} (ID: {group_id})")
                monitor_all = source_data.get('monitor_all', False)
                user_ids = set(source_data.get('user_ids', []))
                source_name = source_data.get('name', str(group_id))

                # Define handler for this specific source
                # We need to capture variables in default args or closure to avoid late binding issues in loop
                # CHANGED: Listen to ALL chats and filter inside to debug ID issues
                @self.client.on(events.NewMessage())
                async def handler(event, s_all=monitor_all, s_users=user_ids, s_name=source_name, s_id=group_id):
                    try:
                        if not self.is_monitoring:
                            return
                        
                        # Filter by Chat ID manually
                        chat_id = event.chat_id
                        if chat_id != s_id:
                            return

                        # self.log_signal.emit(f"[DEBUG] Handler triggered for {s_name}")
                        
                        should_forward = False
                        sender_name = "Unknown"

                        if s_all:
                            should_forward = True
                            try:
                                sender = await event.get_sender()
                                if sender:
                                     sender_name = f"{sender.first_name or ''} {sender.last_name or ''}".strip() or "Unknown"
                                else:
                                     sender_name = "Channel/Anonymous"
                            except:
                                sender_name = "Channel Message" # Common for channels
                        else:
                            sender_id = event.sender_id
                            if sender_id in s_users:
                                should_forward = True
                                try:
                                    sender = await event.get_sender()
                                    if sender:
                                        sender_name = f"{sender.first_name or ''} {sender.last_name or ''}".strip() or "Unknown"
                                except:
                                    pass

                        if should_forward:
                            self.log_signal.emit(f"Scraping message from {sender_name} in {s_name}...")
                            
                            for dest_id in self.destination_ids:
                                try:
                                    # Handle 'me' destination
                                    target = 'me' if dest_id == 'me' else int(dest_id)
                                    
                                    # Use send_message to "scrape" (copy) instead of forward
                                    await self.client.send_message(target, event.message)
                                    
                                    dest_label = "Saved Messages" if dest_id == 'me' else str(dest_id)
                                    self.log_signal.emit(f"Sent to {dest_label}.")
                                    
                                    # Safety delay to prevent flood limits
                                    await asyncio.sleep(random.uniform(0.5, 1.5))
                                except Exception as e:
                                    err_msg = str(e)
                                    self.log_signal.emit(f"❌ Failed to send to {dest_id}: {err_msg}")
                    except Exception as e:
                        self.log_signal.emit(f"Handler Error: {e}")

                self.message_handlers.append(handler)
                
                mode_str = "All Messages" if monitor_all else f"{len(user_ids)} Members"
                self.log_signal.emit(f"Started monitoring {source_name} ({mode_str})")
            
            except Exception as e:
                self.log_signal.emit(f"Error starting monitor for {source_id}: {e}")
        
        # Global debug handler disabled for production
        # @self.client.on(events.NewMessage())
        # async def global_debug_handler(event):
        #     pass

        self.save_targets()



    def register_command_handler(self):
        # Remove existing command handler if any to prevent duplicates
        if hasattr(self, '_command_handler_ref') and self._command_handler_ref:
            self.client.remove_event_handler(self._command_handler_ref)

        @self.client.on(events.NewMessage(chats='me', pattern=r'^\..*'))
        async def command_handler(event):
            await self.handle_command(event)
        
        self._command_handler_ref = command_handler # Store reference

    async def handle_command(self, event):
        text = event.message.text.strip()
        parts = text.split()
        cmd = parts[0].lower()
        
        reply = ""
        
        try:
            if cmd == ".menu" or cmd == ".status" or cmd == ".help":
                status = "🟢 **Running**" if self.is_monitoring else "🔴 **Stopped**"
                
                sources_list = []
                if not self.sources:
                    sources_list.append("No sources configured.")
                else:
                    for sid, data in self.sources.items():
                        s_name = data.get('name', sid)
                        s_all = data.get('monitor_all', False)
                        s_users = len(data.get('user_ids', []))
                        mode = "📨 All" if s_all else f"👤 {s_users} Users"
                        sources_list.append(f"• **{s_name}**: {mode}\n   👉 Edit: `.edit {sid}` | ❌ `.remove {sid}`")

                sources_text = "\n".join(sources_list)
                dest_count = len(self.destination_ids)
                
                reply = (
                    f"🤖 **Multi-Source Dashboard**\n\n"
                    f"**Status:** {status}\n"
                    f"**Destinations:** {dest_count}\n\n"
                    f"**Active Sources:**\n{sources_text}\n\n"
                    f"**Actions:**\n"
                    f"🔹 `.list` - Find Groups to Add\n"
                    f"🔹 `.search <text>` - Search Groups\n"
                    f"🔹 `.add <id>` - Add a Source\n"
                    f"🔹 `.dest` - Manage Destinations\n"
                    f"🔹 `.stop` / `.start` - Control Monitor"
                )

            elif cmd == ".search":
                if len(parts) < 2:
                    reply = "Usage: `.search <text>`"
                else:
                    query = " ".join(parts[1:]).lower()
                    limit = 200 # Fetch more for search
                    dialogs = await self.client.get_dialogs(limit=limit)
                    
                    matches = []
                    for d in dialogs:
                        if (d.is_group or d.is_channel) and query in d.name.lower():
                            matches.append(d)
                    
                    if not matches:
                        reply = f"❌ No groups found matching '{query}'."
                    else:
                        # Limit results
                        matches = matches[:10]
                        lines = [f"**Search Results for '{query}':**"]
                        for d in matches:
                            lines.append(f"🔹 `{d.name}`\n   👉 `.add {d.id}`")
                        
                        if len(matches) == 10:
                            lines.append("\n(Showing top 10 results)")
                        
                        reply = "\n".join(lines)

            elif cmd == ".list":
                page = 1
                if len(parts) > 1:
                    try:
                        page = int(parts[1])
                        if page < 1: page = 1
                    except ValueError:
                        pass
                
                limit = 100
                dialogs = await self.client.get_dialogs(limit=limit)
                valid_dialogs = [d for d in dialogs if d.is_group or d.is_channel]
                
                items_per_page = 10
                total_items = len(valid_dialogs)
                total_pages = (total_items + items_per_page - 1) // items_per_page
                
                if page > total_pages and total_pages > 0: page = total_pages
                start_idx = (page - 1) * items_per_page
                current_page_items = valid_dialogs[start_idx : start_idx + items_per_page]
                
                lines = [f"**Available Sources (Page {page}/{total_pages}):**"]
                for d in current_page_items:
                    lines.append(f"🔹 `{d.name}`\n   👉 `.add {d.id}`")
                
                if page < total_pages:
                    lines.append(f"\n➡️ Next: `.list {page + 1}`")
                
                reply = "\n".join(lines)

            elif cmd == ".add":
                if len(parts) < 2:
                    reply = "Usage: `.add <id>` (Use `.list` to find IDs)"
                else:
                    try:
                        new_id = parts[1] # Keep as string for dict key
                        int_id = int(new_id) # Verify int
                        
                        self.stop_monitoring() # Stop to configure
                        
                        # Fetch info
                        name = str(new_id)
                        is_channel = False
                        try:
                            entity = await self.client.get_entity(int_id)
                            name = entity.title
                            if getattr(entity, 'broadcast', False):
                                is_channel = True
                        except:
                            pass
                        
                        # Initialize default config
                        self.sources[new_id] = {
                            "name": name,
                            "type": "channel" if is_channel else "group",
                            "monitor_all": is_channel, # Default True for channels
                            "user_ids": []
                        }
                        self.current_edit_id = new_id
                        self.save_targets()
                        
                        reply = f"✅ Added **{name}**.\n"
                        reply += f"Currently editing: **{name}**\n\n"
                        
                        if is_channel:
                            reply += "ℹ️ Channel detected. Mode set to **All Messages**.\n"
                            reply += "👉 Type `.start` to begin, or `.add <id>` to add another."
                        else:
                            reply += "👉 Type `.members` to select users.\n"
                            reply += "👉 OR type `.mode` to toggle **All Messages**.\n"
                            reply += "👉 Type `.done` when finished."

                    except ValueError:
                        reply = "❌ Invalid ID."

            elif cmd == ".edit":
                if len(parts) < 2:
                    reply = "Usage: `.edit <id>`"
                else:
                    target_id = parts[1]
                    if target_id in self.sources:
                        self.current_edit_id = target_id
                        self.stop_monitoring()
                        s_name = self.sources[target_id]['name']
                        reply = f"✏️ Editing **{s_name}**.\n"
                        reply += "👉 Type `.members`, `.mode`, or `.remove`."
                    else:
                        reply = "❌ Source not found."

            elif cmd == ".remove":
                target_id = None
                if len(parts) > 1:
                    target_id = parts[1]
                elif self.current_edit_id:
                    target_id = self.current_edit_id
                
                if target_id and target_id in self.sources:
                    name = self.sources[target_id]['name']
                    del self.sources[target_id]
                    if self.current_edit_id == target_id:
                        self.current_edit_id = None
                    self.save_targets()
                    reply = f"🗑️ Removed **{name}**."
                else:
                    reply = "Usage: `.remove <id>`"

            elif cmd == ".mode":
                if not self.current_edit_id or self.current_edit_id not in self.sources:
                    reply = "⚠️ No source selected. Use `.edit <id>` or `.add <id>`."
                else:
                    curr = self.sources[self.current_edit_id]
                    curr['monitor_all'] = not curr['monitor_all']
                    self.save_targets()
                    mode_str = "All Messages" if curr['monitor_all'] else "Selected Members"
                    reply = f"✅ **{curr['name']}** mode: **{mode_str}**"

            elif cmd == ".members":
                if not self.current_edit_id or self.current_edit_id not in self.sources:
                    reply = "⚠️ No source selected. Use `.edit <id>` or `.add <id>`."
                else:
                    page = 1
                    if len(parts) > 1:
                        try:
                            page = int(parts[1])
                            if page < 1: page = 1
                        except ValueError:
                            pass
                    
                    curr_id = int(self.current_edit_id)
                    curr_data = self.sources[self.current_edit_id]
                    current_users = set(curr_data.get('user_ids', []))

                    try:
                        participants = await self.get_participants(curr_id)
                        if not participants:
                            reply = "⚠️ No participants found."
                        else:
                            items_per_page = 10
                            total_items = len(participants)
                            total_pages = (total_items + items_per_page - 1) // items_per_page
                            if page > total_pages and total_pages > 0: page = total_pages
                            
                            start_idx = (page - 1) * items_per_page
                            current_page_items = participants[start_idx : start_idx + items_per_page]
                            
                            lines = [f"**Members of {curr_data['name']} (Page {page}/{total_pages}):**"]
                            for uid, name, username in current_page_items:
                                status = "✅" if uid in current_users else "⬜"
                                action = ".unselect" if uid in current_users else ".select"
                                u_label = f"{name} (@{username})" if username else name
                                lines.append(f"{status} **{u_label}**\n   👉 `{action} {uid}`")
                            
                            if page < total_pages:
                                lines.append(f"\n➡️ Next: `.members {page + 1}`")
                            reply = "\n".join(lines)
                    except Exception as e:
                        reply = f"❌ Error: {e}"

            elif cmd == ".select" or cmd == ".unselect":
                if not self.current_edit_id or self.current_edit_id not in self.sources:
                    reply = "⚠️ No source selected."
                elif len(parts) < 2:
                    reply = f"Usage: `{cmd} <id>`"
                else:
                    try:
                        uid = int(parts[1])
                        curr = self.sources[self.current_edit_id]
                        users = set(curr.get('user_ids', []))
                        
                        if cmd == ".select":
                            users.add(uid)
                            curr['monitor_all'] = False
                            reply = f"✅ Added user `{uid}` to **{curr['name']}**."
                        else:
                            if uid in users:
                                users.remove(uid)
                                reply = f"🗑️ Removed user `{uid}`."
                            else:
                                reply = "⚠️ User not in list."
                        
                        curr['user_ids'] = list(users)
                        self.save_targets()
                    except ValueError:
                        reply = "❌ Invalid ID."
            
            elif cmd == ".done":
                self.current_edit_id = None
                reply = "✅ Configuration saved. Type `.start` to monitor."

            elif cmd == ".dest":
                if len(parts) == 1:
                    lines = ["**Destinations:**"]
                    for d in self.destination_ids:
                         lines.append(f"📍 `{d}` (❌ `.dest del {d}`)")
                    lines.append("\n👉 `.dest add <id>`")
                    reply = "\n".join(lines)
                else:
                    action = parts[1].lower()
                    try:
                        target_id = parts[2]
                        if target_id.lower() == 'me': target_id = 'me'
                        else: target_id = int(target_id)
                        
                        if action == "add":
                            if target_id not in self.destination_ids:
                                self.destination_ids.append(target_id)
                                self.save_targets()
                                reply = f"✅ Added dest `{target_id}`."
                            else: reply = "⚠️ Exists."
                        elif action == "del":
                            if target_id in self.destination_ids:
                                self.destination_ids.remove(target_id)
                                self.save_targets()
                                reply = f"🗑️ Removed dest `{target_id}`."
                            else: reply = "⚠️ Not found."
                    except: reply = "❌ Invalid."

            elif cmd == ".stop":
                self.stop_monitoring()
                reply = "🔴 **Monitoring Stopped.**"

            elif cmd == ".start":
                if not self.sources:
                    reply = "⚠️ No sources. Use `.list` then `.add <id>`."
                else:
                    self.start_monitoring()
                    reply = f"🟢 **Started Monitoring {len(self.sources)} Sources.**"

            else:
                reply = "Unknown command. Type `.menu`."
        
        except Exception as e:
            reply = f"❌ Error executing command: {str(e)}"
        
        await event.reply(reply)

    def load_targets(self):
        if os.path.exists(TARGETS_FILE):
            try:
                with open(TARGETS_FILE, "r") as f:
                    targets = json.load(f)
                    
                    # Handle legacy format migration
                    if "group_id" in targets:
                        self.log_signal.emit("Migrating legacy config...")
                        gid = targets.get("group_id")
                        if gid:
                            self.sources[str(gid)] = {
                                "name": str(gid),
                                "type": "unknown",
                                "monitor_all": targets.get("monitor_all", False),
                                "user_ids": list(targets.get("user_ids", []))
                            }
                    else:
                        self.sources = targets.get("sources", {})

                    self.destination_ids = targets.get("destination_ids", ['me'])
                self.log_signal.emit("Loaded monitoring configuration.")
            except Exception as e:
                self.log_signal.emit(f"Error loading targets: {e}")
        else:
            self.log_signal.emit("No targets.json found.")

    def save_targets(self):
        targets = {
            "sources": self.sources,
            "destination_ids": self.destination_ids
        }
        try:
            with open(TARGETS_FILE, "w") as f:
                json.dump(targets, f, indent=4)
            self.log_signal.emit("Saved configuration.")
        except Exception as e:
            self.log_signal.emit(f"Error saving targets: {e}")

    async def restart_monitoring(self):
        self.stop_monitoring()
        await asyncio.sleep(1)
        if self.sources:
            self.start_monitoring()
        else:
            self.log_signal.emit("Cannot restart: no sources configured.")

    def stop_monitoring(self, keep_running=False):
        if not keep_running:
            self.is_monitoring = False
        if self.client:
            # Remove all registered message handlers
            if hasattr(self, 'message_handlers'):
                for handler in self.message_handlers:
                    self.client.remove_event_handler(handler)
                self.message_handlers = []
            
            # Legacy cleanup
            if hasattr(self, 'message_handler') and self.message_handler:
                self.client.remove_event_handler(self.message_handler)
                self.message_handler = None
        
        self.log_signal.emit("Monitoring stopped.")
