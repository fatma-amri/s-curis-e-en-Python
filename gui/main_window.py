"""
Main window for the secure P2P messenger.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from gui.chat_interface import ChatInterface
from gui.connection_dialog import ConnectionDialog
from gui.settings_window import SettingsWindow
from utils.logger import SecureLogger

logger = SecureLogger('main_window')


class MainWindow:
    """Main application window."""
    
    def __init__(self, app):
        """
        Initialize main window.
        
        Args:
            app: Application instance
        """
        self.app = app
        self.root = tk.Tk()
        self.root.title("Secure P2P Messenger")
        
        # Get window size from config
        width = app.config.get('ui', 'window_width')
        height = app.config.get('ui', 'window_height')
        self.root.geometry(f"{width}x{height}")
        
        self._create_menu()
        self._create_widgets()
        self._create_status_bar()
        
        # Center window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
    
    def _create_menu(self):
        """Create menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Exit", command=self._on_close)
        
        # Connection menu
        connection_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Connection", menu=connection_menu)
        connection_menu.add_command(label="New Connection...", command=self._show_connection_dialog)
        connection_menu.add_command(label="Disconnect", command=self._disconnect)
        connection_menu.add_separator()
        connection_menu.add_command(label="Show Fingerprint", command=self._show_fingerprint)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Settings...", command=self._show_settings)
        tools_menu.add_separator()
        tools_menu.add_command(label="Clear Chat", command=self._clear_chat)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self._show_about)
    
    def _create_widgets(self):
        """Create main widgets."""
        # Main container
        main_container = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - conversations list (future feature, now just a placeholder)
        left_frame = ttk.Frame(main_container, width=200)
        main_container.add(left_frame, weight=0)
        
        ttk.Label(
            left_frame,
            text="Conversations",
            font=('Arial', 12, 'bold')
        ).pack(pady=10)
        
        self.conversations_list = tk.Listbox(left_frame)
        self.conversations_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Right panel - chat interface
        right_frame = ttk.Frame(main_container)
        main_container.add(right_frame, weight=1)
        
        # Chat interface
        self.chat_interface = ChatInterface(right_frame)
        self.chat_interface.set_send_callback(self._send_message)
        self.chat_interface.set_attach_callback(self._attach_file)
        
        # Bind Enter key to send
        self.chat_interface.message_entry.bind('<Return>', self._on_enter_key)
    
    def _create_status_bar(self):
        """Create status bar."""
        status_frame = ttk.Frame(self.root, relief=tk.SUNKEN)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_label = ttk.Label(
            status_frame,
            text="Disconnected",
            font=('Arial', 9)
        )
        self.status_label.pack(side=tk.LEFT, padx=5)
        
        self.connection_info_label = ttk.Label(
            status_frame,
            text="",
            font=('Arial', 9)
        )
        self.connection_info_label.pack(side=tk.RIGHT, padx=5)
    
    def _show_connection_dialog(self):
        """Show connection dialog."""
        dialog = ConnectionDialog(self.root, self.app.key_manager)
        result = dialog.show()
        
        if result:
            if result['mode'] == 'listen':
                self.app.start_server(port=result['port'])
            else:
                self.app.connect_to_peer(result['host'], result['port'])
    
    def _disconnect(self):
        """Disconnect from peer."""
        if self.app.network_manager and self.app.network_manager.is_connected:
            self.app.network_manager.disconnect()
            self.update_status("Disconnected")
            self.chat_interface.enable_input(False)
            messagebox.showinfo("Disconnected", "Disconnected from peer.")
        else:
            messagebox.showinfo("Not Connected", "No active connection.")
    
    def _show_fingerprint(self):
        """Show local fingerprint."""
        fingerprint = self.app.key_manager.get_fingerprint()
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Your Fingerprint")
        dialog.geometry("500x200")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        
        frame = ttk.Frame(dialog, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(
            frame,
            text="Your Fingerprint:",
            font=('Arial', 12, 'bold')
        ).pack(pady=(0, 10))
        
        fp_text = tk.Text(frame, height=3, wrap=tk.WORD, font=('Courier', 10))
        fp_text.insert(1.0, fingerprint)
        fp_text.config(state=tk.DISABLED)
        fp_text.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        ttk.Button(
            frame,
            text="Close",
            command=dialog.destroy
        ).pack()
    
    def _show_settings(self):
        """Show settings window."""
        SettingsWindow(self.root, self.app.config)
    
    def _clear_chat(self):
        """Clear chat display."""
        if messagebox.askyesno("Clear Chat", "Are you sure you want to clear the chat display?"):
            self.chat_interface.clear_messages()
    
    def _show_about(self):
        """Show about dialog."""
        about_text = """Secure P2P Messenger

A peer-to-peer encrypted messaging application with end-to-end encryption.

Features:
• ChaCha20-Poly1305 AEAD encryption
• Ed25519 signatures and X25519 key exchange
• Secure local storage with Argon2id
• Direct P2P connections (no server required)

Authors: Fatma Amri, Mariem Baraket
License: MIT"""
        
        messagebox.showinfo("About", about_text)
    
    def _send_message(self):
        """Send a message."""
        text = self.chat_interface.get_input_text()
        
        if not text:
            return
        
        # Validate message length
        max_length = self.app.config.get('ui', 'message_max_length')
        if len(text) > max_length:
            messagebox.showwarning(
                "Message Too Long",
                f"Message must be less than {max_length} characters."
            )
            return
        
        # Send via network manager
        if self.app.network_manager and self.app.network_manager.is_connected:
            success = self.app.network_manager.send_text_message(text)
            
            if success:
                # Display sent message
                self.chat_interface.add_message(text, 'sent')
                self.chat_interface.clear_input()
                
                # Save to database
                if self.app.conversation_storage:
                    try:
                        self.app.conversation_storage.save_sent_message(text)
                    except Exception as e:
                        logger.error(f"Failed to save message: {e}")
            else:
                messagebox.showerror("Send Failed", "Failed to send message.")
        else:
            messagebox.showwarning("Not Connected", "No active connection.")
    
    def _attach_file(self):
        """Attach and send a file."""
        if not self.app.network_manager or not self.app.network_manager.is_connected:
            messagebox.showwarning("Not Connected", "No active connection.")
            return
        
        # Select file
        file_path = filedialog.askopenfilename(
            title="Select File to Send",
            filetypes=[("All Files", "*.*")]
        )
        
        if file_path:
            try:
                # Prepare file
                filename, size, hash_val, data = self.app.file_storage.prepare_file_for_sending(file_path)
                
                messagebox.showinfo(
                    "File Transfer",
                    f"File transfer feature is implemented but requires additional protocol support.\n\n"
                    f"File: {filename}\nSize: {size} bytes"
                )
                
            except Exception as e:
                messagebox.showerror("File Error", f"Error preparing file: {e}")
    
    def _on_enter_key(self, event):
        """Handle Enter key in message entry."""
        # Shift+Enter for new line, Enter alone to send
        if event.state & 0x1:  # Shift key
            return
        else:
            self._send_message()
            return 'break'  # Prevent default behavior
    
    def _on_close(self):
        """Handle window close."""
        if self.app.network_manager and self.app.network_manager.is_connected:
            if messagebox.askyesno("Quit", "You are currently connected. Disconnect and quit?"):
                self.app.shutdown()
                self.root.destroy()
        else:
            self.app.shutdown()
            self.root.destroy()
    
    def update_status(self, status, info=""):
        """
        Update status bar.
        
        Args:
            status: Status text
            info: Additional info text
        """
        self.status_label.config(text=status)
        self.connection_info_label.config(text=info)
    
    def display_received_message(self, text):
        """
        Display a received message.
        
        Args:
            text: Message text
        """
        self.chat_interface.add_message(text, 'received')
        
        # Save to database
        if self.app.conversation_storage:
            try:
                self.app.conversation_storage.save_received_message(text)
            except Exception as e:
                logger.error(f"Failed to save message: {e}")
    
    def enable_chat(self, enabled=True):
        """
        Enable or disable chat interface.
        
        Args:
            enabled: True to enable, False to disable
        """
        self.chat_interface.enable_input(enabled)
    
    def run(self):
        """Run the main event loop."""
        self.root.mainloop()
