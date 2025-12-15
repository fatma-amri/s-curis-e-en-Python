"""
Connection dialog for the P2P messenger.
Allows user to choose between server and client mode.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from utils.validators import validate_ip, validate_port
from gui.styles import COLORS, FONTS, ICONS


class ConnectionDialog:
    """Dialog for establishing P2P connections."""
    
    def __init__(self, parent, key_manager):
        """
        Initialize connection dialog.
        
        Args:
            parent: Parent window
            key_manager: KeyManager instance for displaying fingerprint
        """
        self.parent = parent
        self.key_manager = key_manager
        self.result = None
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(f"{ICONS['connect']} Connexion P2P")
        self.dialog.geometry("500x450")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.configure(bg=COLORS['background'])
        
        self._create_widgets()
        
        # Bind Escape key
        self.dialog.bind('<Escape>', lambda e: self._on_cancel())
        
        # Center dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (450 // 2)
        self.dialog.geometry(f"500x450+{x}+{y}")
    
    def _create_widgets(self):
        """Create dialog widgets."""
        # Main frame
        main_frame = tk.Frame(self.dialog, padding=20, bg=COLORS['background'])
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = tk.Label(
            main_frame,
            text=f"{ICONS['connect']} Établir une connexion sécurisée",
            font=FONTS['title'],
            fg=COLORS['text_primary'],
            bg=COLORS['background']
        )
        title_label.pack(pady=(0, 20))
        
        # Mode selection with cards
        mode_label = tk.Label(
            main_frame,
            text="Mode de connexion:",
            font=FONTS['heading'],
            fg=COLORS['text_primary'],
            bg=COLORS['background'],
            anchor=tk.W
        )
        mode_label.pack(fill=tk.X, pady=(0, 10))
        
        mode_frame = tk.Frame(main_frame, bg=COLORS['background'])
        mode_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.mode_var = tk.StringVar(value="listen")
        
        # Listen mode card
        listen_card = tk.Frame(mode_frame, bg=COLORS['secondary'], relief=tk.FLAT, bd=2)
        listen_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        listen_radio = tk.Radiobutton(
            listen_card,
            text=f"{ICONS['listen']} Écouter\n(Serveur)",
            variable=self.mode_var,
            value="listen",
            command=self._on_mode_change,
            font=FONTS['body'],
            bg=COLORS['secondary'],
            fg=COLORS['text_primary'],
            selectcolor=COLORS['secondary'],
            activebackground=COLORS['secondary'],
            pady=15,
            padx=10,
            bd=0,
            cursor='hand2'
        )
        listen_radio.pack(fill=tk.BOTH, expand=True)
        
        # Connect mode card
        connect_card = tk.Frame(mode_frame, bg=COLORS['secondary'], relief=tk.FLAT, bd=2)
        connect_card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        connect_radio = tk.Radiobutton(
            connect_card,
            text=f"{ICONS['connect']} Se connecter\n(Client)",
            variable=self.mode_var,
            value="connect",
            command=self._on_mode_change,
            font=FONTS['body'],
            bg=COLORS['secondary'],
            fg=COLORS['text_primary'],
            selectcolor=COLORS['secondary'],
            activebackground=COLORS['secondary'],
            pady=15,
            padx=10,
            bd=0,
            cursor='hand2'
        )
        connect_radio.pack(fill=tk.BOTH, expand=True)
        
        # Connection details
        details_frame = tk.LabelFrame(
            main_frame,
            text=" Paramètres ",
            font=FONTS['body'],
            fg=COLORS['text_primary'],
            bg=COLORS['background'],
            relief=tk.SOLID,
            bd=1
        )
        details_frame.pack(fill=tk.X, pady=(0, 15))
        
        inner_frame = tk.Frame(details_frame, bg=COLORS['background'])
        inner_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # IP Address (only for client mode)
        ip_frame = tk.Frame(inner_frame, bg=COLORS['background'])
        ip_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.ip_label = tk.Label(
            ip_frame,
            text="Adresse IP:",
            width=12,
            font=FONTS['body'],
            fg=COLORS['text_primary'],
            bg=COLORS['background'],
            anchor=tk.W
        )
        self.ip_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.ip_entry = tk.Entry(
            ip_frame,
            font=FONTS['body'],
            bg=COLORS['background'],
            fg=COLORS['text_primary'],
            relief=tk.SOLID,
            bd=1
        )
        self.ip_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.ip_entry.insert(0, "127.0.0.1")
        
        # Port
        port_frame = tk.Frame(inner_frame, bg=COLORS['background'])
        port_frame.pack(fill=tk.X)
        
        tk.Label(
            port_frame,
            text="Port:",
            width=12,
            font=FONTS['body'],
            fg=COLORS['text_primary'],
            bg=COLORS['background'],
            anchor=tk.W
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.port_entry = tk.Entry(
            port_frame,
            font=FONTS['body'],
            bg=COLORS['background'],
            fg=COLORS['text_primary'],
            relief=tk.SOLID,
            bd=1
        )
        self.port_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.port_entry.insert(0, "5555")
        
        # Fingerprint display
        fp_frame = tk.LabelFrame(
            main_frame,
            text=" Votre identité ",
            font=FONTS['body'],
            fg=COLORS['text_primary'],
            bg=COLORS['background'],
            relief=tk.SOLID,
            bd=1
        )
        fp_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        fp_inner = tk.Frame(fp_frame, bg=COLORS['background'])
        fp_inner.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        tk.Label(
            fp_inner,
            text="Fingerprint:",
            font=FONTS['body'],
            fg=COLORS['text_primary'],
            bg=COLORS['background'],
            anchor=tk.W
        ).pack(fill=tk.X, pady=(0, 5))
        
        fingerprint = self.key_manager.get_fingerprint()
        
        fp_display_frame = tk.Frame(fp_inner, bg=COLORS['secondary'], relief=tk.FLAT, bd=1)
        fp_display_frame.pack(fill=tk.BOTH, expand=True)
        
        fp_text = tk.Text(
            fp_display_frame,
            height=2,
            wrap=tk.WORD,
            font=FONTS['mono_small'],
            bg=COLORS['secondary'],
            fg=COLORS['text_primary'],
            relief=tk.FLAT,
            bd=8
        )
        fp_text.insert(1.0, fingerprint)
        fp_text.config(state=tk.DISABLED)
        fp_text.pack(fill=tk.BOTH, expand=True)
        
        # Buttons
        button_frame = tk.Frame(main_frame, bg=COLORS['background'])
        button_frame.pack(fill=tk.X)
        
        cancel_btn = tk.Button(
            button_frame,
            text="Annuler",
            command=self._on_cancel,
            font=FONTS['body'],
            bg=COLORS['secondary'],
            fg=COLORS['text_primary'],
            relief=tk.FLAT,
            bd=0,
            padx=20,
            pady=10,
            cursor='hand2'
        )
        cancel_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        connect_btn = tk.Button(
            button_frame,
            text=f"Connecter {ICONS['rocket']}",
            command=self._on_connect,
            font=FONTS['body'],
            bg=COLORS['primary'],
            fg='white',
            relief=tk.FLAT,
            bd=0,
            padx=20,
            pady=10,
            cursor='hand2'
        )
        connect_btn.pack(side=tk.RIGHT)
        
        # Initial state
        self._on_mode_change()
    
    def _on_mode_change(self):
        """Handle mode change."""
        if self.mode_var.get() == "listen":
            self.ip_entry.config(state=tk.DISABLED)
            self.ip_label.config(state=tk.DISABLED)
        else:
            self.ip_entry.config(state=tk.NORMAL)
            self.ip_label.config(state=tk.NORMAL)
    
    def _on_connect(self):
        """Handle connect button."""
        mode = self.mode_var.get()
        port = self.port_entry.get().strip()
        
        # Validate port
        if not validate_port(port):
            messagebox.showerror("Invalid Input", "Please enter a valid port (1-65535)")
            return
        
        port = int(port)
        
        if mode == "connect":
            ip = self.ip_entry.get().strip()
            
            # Validate IP
            if not validate_ip(ip):
                messagebox.showerror("Invalid Input", "Please enter a valid IP address")
                return
            
            self.result = {"mode": "connect", "host": ip, "port": port}
        else:
            self.result = {"mode": "listen", "port": port}
        
        self.dialog.destroy()
    
    def _on_cancel(self):
        """Handle cancel button."""
        self.result = None
        self.dialog.destroy()
    
    def show(self):
        """
        Show dialog and wait for result.
        
        Returns:
            dict: Connection details or None if cancelled
        """
        self.dialog.wait_window()
        return self.result
