"""
Main window for the secure P2P messenger.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from gui.chat_interface import ChatInterface
from gui.connection_dialog import ConnectionDialog
from gui.settings_window import SettingsWindow
from gui.widgets import StatusBar, ConversationCard
from gui.styles import COLORS, FONTS, STYLES, ICONS
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
        self.root.title(f"{ICONS['lock']} Secure P2P Messenger")
        
        # Get window size from config or use defaults
        width = STYLES['window']['default_width']
        height = STYLES['window']['default_height']
        try:
            width = app.config.get('ui', 'window_width')
            height = app.config.get('ui', 'window_height')
        except:
            pass
        
        self.root.geometry(f"{width}x{height}")
        
        # Set minimum window size
        self.root.minsize(
            STYLES['window']['min_width'],
            STYLES['window']['min_height']
        )
        
        # Set background color
        self.root.configure(bg=COLORS['background'])
        
        self._create_menu()
        self._create_widgets()
        self._create_status_bar()
        
        # Keyboard shortcuts
        self._setup_shortcuts()
        
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
        menubar.add_cascade(label="Fichier", menu=file_menu)
        file_menu.add_command(label="Nouveau", command=self._new_conversation, accelerator="Ctrl+N")
        file_menu.add_command(label="Exporter la conversation", command=self._export_conversation)
        file_menu.add_separator()
        file_menu.add_command(label="Quitter", command=self._on_close, accelerator="Ctrl+Q")
        
        # Connection menu
        connection_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Connexion", menu=connection_menu)
        connection_menu.add_command(label=f"{ICONS['listen']} Écouter", command=self._listen_mode)
        connection_menu.add_command(label=f"{ICONS['connect']} Se connecter", command=self._show_connection_dialog)
        connection_menu.add_command(label="Déconnecter", command=self._disconnect)
        connection_menu.add_separator()
        connection_menu.add_command(label="Afficher le Fingerprint", command=self._show_fingerprint)
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Outils", menu=tools_menu)
        tools_menu.add_command(label=f"{ICONS['settings']} Paramètres", command=self._show_settings)
        tools_menu.add_separator()
        tools_menu.add_command(label="Vérifier Fingerprint", command=self._verify_fingerprint)
        tools_menu.add_command(label="Générer nouvelles clés", command=self._regenerate_keys)
        tools_menu.add_separator()
        tools_menu.add_command(label="Effacer le chat", command=self._clear_chat)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Aide", menu=help_menu)
        help_menu.add_command(label=f"{ICONS['info']} À propos", command=self._show_about)
        help_menu.add_command(label="Documentation", command=self._show_documentation)
    
    def _create_widgets(self):
        """Create main widgets."""
        # Main container with PanedWindow for resizable sidebar
        main_container = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - conversations list
        left_frame = tk.Frame(
            main_container, 
            width=STYLES['sidebar']['width'],
            bg=COLORS['sidebar'],
            relief=tk.FLAT
        )
        main_container.add(left_frame, weight=0)
        
        # Search bar
        search_frame = tk.Frame(left_frame, bg=COLORS['sidebar'])
        search_frame.pack(fill=tk.X, padx=10, pady=10)
        
        search_icon = tk.Label(
            search_frame,
            text=ICONS['search'],
            font=FONTS['body'],
            bg=COLORS['sidebar'],
            fg=COLORS['text_secondary']
        )
        search_icon.pack(side=tk.LEFT, padx=(0, 5))
        
        self.search_entry = tk.Entry(
            search_frame,
            font=FONTS['body'],
            bg=COLORS['background'],
            fg=COLORS['text_primary'],
            relief=tk.FLAT,
            bd=1
        )
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.search_entry.insert(0, "Rechercher...")
        self.search_entry.bind('<FocusIn>', self._on_search_focus_in)
        self.search_entry.bind('<FocusOut>', self._on_search_focus_out)
        
        # Conversations label
        conv_label = tk.Label(
            left_frame,
            text=f"{ICONS['contact']} Conversations",
            font=FONTS['heading'],
            fg=COLORS['text_primary'],
            bg=COLORS['sidebar'],
            anchor=tk.W
        )
        conv_label.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # Conversations list container with scrollbar
        list_container = tk.Frame(left_frame, bg=COLORS['sidebar'])
        list_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        scrollbar = ttk.Scrollbar(list_container)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.conversations_canvas = tk.Canvas(
            list_container,
            bg=COLORS['sidebar'],
            highlightthickness=0,
            yscrollcommand=scrollbar.set
        )
        self.conversations_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.conversations_canvas.yview)
        
        self.conversations_frame = tk.Frame(self.conversations_canvas, bg=COLORS['sidebar'])
        self.conversations_canvas_window = self.conversations_canvas.create_window(
            0, 0,
            window=self.conversations_frame,
            anchor=tk.NW
        )
        
        self.conversations_frame.bind('<Configure>', 
            lambda e: self.conversations_canvas.configure(scrollregion=self.conversations_canvas.bbox('all')))
        self.conversations_canvas.bind('<Configure>',
            lambda e: self.conversations_canvas.itemconfig(self.conversations_canvas_window, width=e.width))
        
        # New conversation button at bottom
        new_conv_btn = tk.Button(
            left_frame,
            text="+ Nouvelle conversation",
            font=FONTS['body'],
            bg=COLORS['primary'],
            fg='white',
            relief=tk.FLAT,
            bd=0,
            padx=15,
            pady=10,
            cursor='hand2',
            command=self._new_conversation
        )
        new_conv_btn.pack(fill=tk.X, padx=10, pady=10)
        
        # Right panel - chat interface
        right_frame = tk.Frame(main_container, bg=COLORS['background'])
        main_container.add(right_frame, weight=1)
        
        # Chat interface
        self.chat_interface = ChatInterface(right_frame)
        self.chat_interface.set_send_callback(self._send_message)
        self.chat_interface.set_attach_callback(self._attach_file)
        
        # Bind Enter key to send
        self.chat_interface.message_entry.bind('<Return>', self._on_enter_key)
        
        # Store main container for later access
        self.main_container = main_container
    
    def _create_status_bar(self):
        """Create status bar."""
        self.status_bar = StatusBar(self.root, bg=COLORS['background'])
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def _show_connection_dialog(self):
        """Show connection dialog."""
        dialog = ConnectionDialog(self.root, self.app.key_manager)
        result = dialog.show()
        
        if result:
            if result['mode'] == 'listen':
                self.app.start_server(port=result['port'])
            else:
                self.app.connect_to_peer(result['host'], result['port'])
    
    def _listen_mode(self):
        """Start listening in server mode."""
        # Use default port from config
        port = self.app.config.get('network', 'default_port')
        self.app.start_server(port=port)
    
    def _new_conversation(self):
        """Start a new conversation (show connection dialog)."""
        self._show_connection_dialog()
    
    def _on_search_focus_in(self, event):
        """Handle search field focus in."""
        if self.search_entry.get() == "Rechercher...":
            self.search_entry.delete(0, tk.END)
            self.search_entry.config(fg=COLORS['text_primary'])
    
    def _on_search_focus_out(self, event):
        """Handle search field focus out."""
        if not self.search_entry.get():
            self.search_entry.insert(0, "Rechercher...")
            self.search_entry.config(fg=COLORS['text_secondary'])
    
    def _setup_shortcuts(self):
        """Setup keyboard shortcuts."""
        self.root.bind('<Control-q>', lambda e: self._on_close())
        self.root.bind('<Control-n>', lambda e: self._new_conversation())
        self.root.bind('<Escape>', lambda e: None)  # Close dialogs handled individually
    
    def _disconnect(self):
        """Disconnect from peer."""
        if self.app.network_manager and self.app.network_manager.is_connected:
            self.app.network_manager.disconnect()
            self.update_status("Déconnecté")
            self.chat_interface.enable_input(False)
            messagebox.showinfo("Déconnecté", "Déconnecté du pair.")
        else:
            messagebox.showinfo("Non connecté", "Aucune connexion active.")
    
    def _verify_fingerprint(self):
        """Verify peer fingerprint."""
        if self.app.network_manager and self.app.network_manager.is_connected:
            peer_fingerprint = self.app.network_manager.get_peer_fingerprint()
            if peer_fingerprint:
                messagebox.showinfo(
                    "Fingerprint du pair",
                    f"Vérifiez ce fingerprint avec votre contact:\n\n{peer_fingerprint}"
                )
            else:
                messagebox.showwarning("Erreur", "Impossible de récupérer le fingerprint du pair.")
        else:
            messagebox.showinfo("Non connecté", "Aucune connexion active.")
    
    def _regenerate_keys(self):
        """Regenerate cryptographic keys (warning!)."""
        result = messagebox.askyesnocancel(
            "Régénérer les clés",
            "⚠️ ATTENTION ⚠️\n\n"
            "Régénérer vos clés changera votre identité et fingerprint.\n"
            "Vous ne pourrez plus vous connecter avec vos contacts existants.\n\n"
            "Êtes-vous sûr de vouloir continuer?"
        )
        if result:
            messagebox.showinfo(
                "Non implémenté",
                "La régénération de clés nécessite un redémarrage de l'application.\n"
                "Pour l'instant, supprimez manuellement le dossier data/keys/ et redémarrez."
            )
    
    def _export_conversation(self):
        """Export conversation to file."""
        messagebox.showinfo(
            "Export",
            "Fonctionnalité à implémenter:\n"
            "Export de la conversation en format texte ou JSON."
        )
    
    def _show_documentation(self):
        """Show documentation."""
        messagebox.showinfo(
            "Documentation",
            "Documentation disponible dans le fichier README.md du projet.\n\n"
            "Visitez: https://github.com/fatma-amri/s-curis-e-en-Python"
        )
    
    def _show_fingerprint(self):
        """Show local fingerprint."""
        fingerprint = self.app.key_manager.get_fingerprint()
        
        dialog = tk.Toplevel(self.root)
        dialog.title("Votre Fingerprint")
        dialog.geometry("550x250")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.configure(bg=COLORS['background'])
        
        frame = tk.Frame(dialog, bg=COLORS['background'])
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        title_label = tk.Label(
            frame,
            text=f"{ICONS['lock']} Votre Fingerprint:",
            font=FONTS['title'],
            fg=COLORS['text_primary'],
            bg=COLORS['background']
        )
        title_label.pack(pady=(0, 15))
        
        fp_frame = tk.Frame(frame, bg=COLORS['secondary'], relief=tk.FLAT, bd=1)
        fp_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        fp_text = tk.Text(
            fp_frame, 
            height=3, 
            wrap=tk.WORD, 
            font=FONTS['mono'],
            bg=COLORS['secondary'],
            fg=COLORS['text_primary'],
            relief=tk.FLAT,
            bd=10
        )
        fp_text.insert(1.0, fingerprint)
        fp_text.config(state=tk.DISABLED)
        fp_text.pack(fill=tk.BOTH, expand=True)
        
        button_frame = tk.Frame(frame, bg=COLORS['background'])
        button_frame.pack(fill=tk.X)
        
        copy_btn = tk.Button(
            button_frame,
            text=f"{ICONS['copy']} Copier",
            font=FONTS['body'],
            bg=COLORS['primary'],
            fg='white',
            relief=tk.FLAT,
            bd=0,
            padx=15,
            pady=8,
            cursor='hand2',
            command=lambda: self._copy_to_clipboard(fingerprint)
        )
        copy_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        close_btn = tk.Button(
            button_frame,
            text="Fermer",
            font=FONTS['body'],
            bg=COLORS['secondary'],
            fg=COLORS['text_primary'],
            relief=tk.FLAT,
            bd=0,
            padx=15,
            pady=8,
            cursor='hand2',
            command=dialog.destroy
        )
        close_btn.pack(side=tk.LEFT)
        
        # Bind Escape key
        dialog.bind('<Escape>', lambda e: dialog.destroy())
    
    def _copy_to_clipboard(self, text):
        """Copy text to clipboard."""
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        messagebox.showinfo("Copié", "Fingerprint copié dans le presse-papiers!")
    
    def _show_settings(self):
        """Show settings window."""
        SettingsWindow(self.root, self.app.config)
    
    def _clear_chat(self):
        """Clear chat display."""
        if messagebox.askyesno("Effacer le chat", "Êtes-vous sûr de vouloir effacer l'affichage du chat?"):
            self.chat_interface.clear_messages()
    
    def _show_about(self):
        """Show about dialog."""
        about_text = f"""{ICONS['lock']} Secure P2P Messenger

Une application de messagerie P2P chiffrée avec chiffrement de bout en bout.

Fonctionnalités:
• Chiffrement ChaCha20-Poly1305 AEAD
• Signatures Ed25519 et échange de clés X25519
• Stockage local sécurisé avec Argon2id
• Connexions P2P directes (sans serveur)

Auteurs: Fatma Amri, Mariem Baraket
Licence: MIT"""
        
        messagebox.showinfo("À propos", about_text)
    
    def _send_message(self):
        """Send a message."""
        text = self.chat_interface.get_input_text()
        
        if not text:
            return
        
        # Validate message length
        try:
            max_length = self.app.config.get('ui', 'message_max_length')
        except Exception:
            max_length = 5000  # Default fallback
            
        if len(text) > max_length:
            messagebox.showwarning(
                "Message trop long",
                f"Le message doit faire moins de {max_length} caractères."
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
                messagebox.showerror("Échec de l'envoi", "Impossible d'envoyer le message.")
        else:
            messagebox.showwarning("Non connecté", "Aucune connexion active.")
    
    def _attach_file(self):
        """Attach and send a file."""
        if not self.app.network_manager or not self.app.network_manager.is_connected:
            messagebox.showwarning("Non connecté", "Aucune connexion active.")
            return
        
        # Select file
        file_path = filedialog.askopenfilename(
            title="Sélectionner un fichier à envoyer",
            filetypes=[("Tous les fichiers", "*.*")]
        )
        
        if file_path:
            try:
                # Prepare file
                filename, size, hash_val, data = self.app.file_storage.prepare_file_for_sending(file_path)
                
                messagebox.showinfo(
                    "Transfert de fichier",
                    f"La fonctionnalité de transfert de fichiers est implémentée mais nécessite un support de protocole supplémentaire.\n\n"
                    f"Fichier: {filename}\nTaille: {size} octets"
                )
                
            except Exception as e:
                messagebox.showerror("Erreur de fichier", f"Erreur lors de la préparation du fichier: {e}")
    
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
            info: Additional info text (host:port)
        """
        # Parse info for IP and port
        ip = ""
        port = ""
        if info and ':' in info:
            parts = info.split(':')
            if len(parts) == 2:
                # Remove "Port: " prefix if present
                ip = parts[0].replace("Port: ", "").strip()
                port = parts[1].strip()
        
        self.status_bar.update_status(status, ip, port)
    
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
