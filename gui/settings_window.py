"""
Settings window for the P2P messenger.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from gui.styles import COLORS, FONTS, ICONS


class SettingsWindow:
    """Settings window for application configuration."""
    
    def __init__(self, parent, config):
        """
        Initialize settings window.
        
        Args:
            parent: Parent window
            config: Config instance
        """
        self.parent = parent
        self.config = config
        
        self.window = tk.Toplevel(parent)
        self.window.title(f"{ICONS['settings']} Paramètres")
        self.window.geometry("550x500")
        self.window.resizable(False, False)
        self.window.transient(parent)
        self.window.grab_set()
        self.window.configure(bg=COLORS['background'])
        
        self._create_widgets()
        
        # Bind Escape key
        self.window.bind('<Escape>', lambda e: self.window.destroy())
        
        # Center window
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (550 // 2)
        y = (self.window.winfo_screenheight() // 2) - (500 // 2)
        self.window.geometry(f"550x500+{x}+{y}")
    
    def _create_widgets(self):
        """Create settings widgets."""
        # Main frame
        main_frame = tk.Frame(self.window, padding=20, bg=COLORS['background'])
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = tk.Label(
            main_frame,
            text=f"{ICONS['settings']} Paramètres de l'application",
            font=FONTS['title'],
            fg=COLORS['text_primary'],
            bg=COLORS['background']
        )
        title_label.pack(pady=(0, 20))
        
        # Notebook for tabbed settings
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # General settings tab
        general_frame = tk.Frame(notebook, bg=COLORS['background'])
        notebook.add(general_frame, text="Général")
        self._create_general_settings(general_frame)
        
        # Network settings tab
        network_frame = tk.Frame(notebook, bg=COLORS['background'])
        notebook.add(network_frame, text="Réseau")
        self._create_network_settings(network_frame)
        
        # Security settings tab
        security_frame = tk.Frame(notebook, bg=COLORS['background'])
        notebook.add(security_frame, text="Sécurité")
        self._create_security_settings(security_frame)
        
        # UI settings tab
        ui_frame = tk.Frame(notebook, bg=COLORS['background'])
        notebook.add(ui_frame, text="Interface")
        self._create_ui_settings(ui_frame)
        
        # Storage settings tab
        storage_frame = tk.Frame(notebook, bg=COLORS['background'])
        notebook.add(storage_frame, text="Stockage")
        self._create_storage_settings(storage_frame)
        
        # Buttons
        button_frame = tk.Frame(main_frame, bg=COLORS['background'])
        button_frame.pack(fill=tk.X)
        
        cancel_btn = tk.Button(
            button_frame,
            text="Annuler",
            command=self.window.destroy,
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
        
        save_btn = tk.Button(
            button_frame,
            text="Enregistrer",
            command=self._save_settings,
            font=FONTS['body'],
            bg=COLORS['primary'],
            fg='white',
            relief=tk.FLAT,
            bd=0,
            padx=20,
            pady=10,
            cursor='hand2'
        )
        save_btn.pack(side=tk.RIGHT)
    
    def _create_general_settings(self, parent):
        """Create general settings."""
        inner = tk.Frame(parent, bg=COLORS['background'], padx=15, pady=15)
        inner.pack(fill=tk.BOTH, expand=True)
        
        # Theme selection (placeholder for future implementation)
        theme_frame = tk.Frame(inner, bg=COLORS['background'])
        theme_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(
            theme_frame,
            text="Thème:",
            width=20,
            font=FONTS['body'],
            fg=COLORS['text_primary'],
            bg=COLORS['background'],
            anchor=tk.W
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.theme_var = tk.StringVar(value="Clair")
        theme_combo = ttk.Combobox(
            theme_frame,
            textvariable=self.theme_var,
            values=["Clair", "Sombre"],
            state="readonly",
            font=FONTS['body']
        )
        theme_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Notifications
        notif_frame = tk.Frame(inner, bg=COLORS['background'])
        notif_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.notifications_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            notif_frame,
            text="Activer les notifications",
            variable=self.notifications_var,
            font=FONTS['body'],
            fg=COLORS['text_primary'],
            bg=COLORS['background'],
            selectcolor=COLORS['background'],
            activebackground=COLORS['background']
        ).pack(anchor=tk.W)
        
        # Auto-start
        autostart_frame = tk.Frame(inner, bg=COLORS['background'])
        autostart_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.autostart_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            autostart_frame,
            text="Démarrer avec le système",
            variable=self.autostart_var,
            font=FONTS['body'],
            fg=COLORS['text_primary'],
            bg=COLORS['background'],
            selectcolor=COLORS['background'],
            activebackground=COLORS['background']
        ).pack(anchor=tk.W)
        
        # Info
        info_label = tk.Label(
            inner,
            text="Note: Les paramètres généraux prennent effet immédiatement.",
            font=FONTS['small'],
            fg=COLORS['text_secondary'],
            bg=COLORS['background'],
            wraplength=450,
            justify=tk.LEFT
        )
        info_label.pack(pady=(20, 0), anchor=tk.W)
    
    def _create_network_settings(self, parent):
        """Create network settings."""
        inner = tk.Frame(parent, bg=COLORS['background'], padx=15, pady=15)
        inner.pack(fill=tk.BOTH, expand=True)
        
        # Default port
        port_frame = tk.Frame(inner, bg=COLORS['background'])
        port_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(
            port_frame,
            text="Port par défaut:",
            width=20,
            font=FONTS['body'],
            fg=COLORS['text_primary'],
            bg=COLORS['background'],
            anchor=tk.W
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.port_var = tk.StringVar(
            value=str(self.config.get('network', 'default_port'))
        )
        tk.Entry(
            port_frame,
            textvariable=self.port_var,
            font=FONTS['body'],
            bg=COLORS['background'],
            fg=COLORS['text_primary'],
            relief=tk.SOLID,
            bd=1
        ).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Connection timeout
        timeout_frame = tk.Frame(inner, bg=COLORS['background'])
        timeout_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(
            timeout_frame,
            text="Timeout connexion (s):",
            width=20,
            font=FONTS['body'],
            fg=COLORS['text_primary'],
            bg=COLORS['background'],
            anchor=tk.W
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.timeout_var = tk.StringVar(
            value=str(self.config.get('network', 'connection_timeout'))
        )
        tk.Entry(
            timeout_frame,
            textvariable=self.timeout_var,
            font=FONTS['body'],
            bg=COLORS['background'],
            fg=COLORS['text_primary'],
            relief=tk.SOLID,
            bd=1
        ).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Heartbeat interval
        heartbeat_frame = tk.Frame(inner, bg=COLORS['background'])
        heartbeat_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(
            heartbeat_frame,
            text="Intervalle heartbeat (s):",
            width=20,
            font=FONTS['body'],
            fg=COLORS['text_primary'],
            bg=COLORS['background'],
            anchor=tk.W
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.heartbeat_var = tk.StringVar(
            value=str(self.config.get('network', 'heartbeat_interval'))
        )
        tk.Entry(
            heartbeat_frame,
            textvariable=self.heartbeat_var,
            font=FONTS['body'],
            bg=COLORS['background'],
            fg=COLORS['text_primary'],
            relief=tk.SOLID,
            bd=1
        ).pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    def _create_security_settings(self, parent):
        """Create security settings."""
        inner = tk.Frame(parent, bg=COLORS['background'], padx=15, pady=15)
        inner.pack(fill=tk.BOTH, expand=True)
        
        # Rekeying threshold
        rekey_msg_frame = tk.Frame(inner, bg=COLORS['background'])
        rekey_msg_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(
            rekey_msg_frame,
            text="Rekey après messages:",
            width=20,
            font=FONTS['body'],
            fg=COLORS['text_primary'],
            bg=COLORS['background'],
            anchor=tk.W
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.rekey_msg_var = tk.StringVar(
            value=str(self.config.get('security', 'rekeying_message_threshold'))
        )
        tk.Entry(
            rekey_msg_frame,
            textvariable=self.rekey_msg_var,
            font=FONTS['body'],
            bg=COLORS['background'],
            fg=COLORS['text_primary'],
            relief=tk.SOLID,
            bd=1
        ).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Rekeying time threshold
        rekey_time_frame = tk.Frame(inner, bg=COLORS['background'])
        rekey_time_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(
            rekey_time_frame,
            text="Rekey après temps (s):",
            width=20,
            font=FONTS['body'],
            fg=COLORS['text_primary'],
            bg=COLORS['background'],
            anchor=tk.W
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.rekey_time_var = tk.StringVar(
            value=str(self.config.get('security', 'rekeying_time_threshold'))
        )
        tk.Entry(
            rekey_time_frame,
            textvariable=self.rekey_time_var,
            font=FONTS['body'],
            bg=COLORS['background'],
            fg=COLORS['text_primary'],
            relief=tk.SOLID,
            bd=1
        ).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Auto fingerprint verification
        verify_frame = tk.Frame(inner, bg=COLORS['background'])
        verify_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.auto_verify_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            verify_frame,
            text="Vérification automatique du fingerprint",
            variable=self.auto_verify_var,
            font=FONTS['body'],
            fg=COLORS['text_primary'],
            bg=COLORS['background'],
            selectcolor=COLORS['background'],
            activebackground=COLORS['background']
        ).pack(anchor=tk.W)
        
        # Info label
        info_label = tk.Label(
            inner,
            text="Note: Les paramètres de sécurité prennent effet à la prochaine connexion.",
            font=FONTS['small'],
            fg=COLORS['text_secondary'],
            bg=COLORS['background'],
            wraplength=450,
            justify=tk.LEFT
        )
        info_label.pack(pady=(20, 0), anchor=tk.W)
    
    def _create_ui_settings(self, parent):
        """Create UI settings."""
        inner = tk.Frame(parent, bg=COLORS['background'], padx=15, pady=15)
        inner.pack(fill=tk.BOTH, expand=True)
        
        # Window dimensions
        width_frame = tk.Frame(inner, bg=COLORS['background'])
        width_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(
            width_frame,
            text="Largeur fenêtre:",
            width=20,
            font=FONTS['body'],
            fg=COLORS['text_primary'],
            bg=COLORS['background'],
            anchor=tk.W
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.width_var = tk.StringVar(
            value=str(self.config.get('ui', 'window_width'))
        )
        tk.Entry(
            width_frame,
            textvariable=self.width_var,
            font=FONTS['body'],
            bg=COLORS['background'],
            fg=COLORS['text_primary'],
            relief=tk.SOLID,
            bd=1
        ).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        height_frame = tk.Frame(inner, bg=COLORS['background'])
        height_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(
            height_frame,
            text="Hauteur fenêtre:",
            width=20,
            font=FONTS['body'],
            fg=COLORS['text_primary'],
            bg=COLORS['background'],
            anchor=tk.W
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.height_var = tk.StringVar(
            value=str(self.config.get('ui', 'window_height'))
        )
        tk.Entry(
            height_frame,
            textvariable=self.height_var,
            font=FONTS['body'],
            bg=COLORS['background'],
            fg=COLORS['text_primary'],
            relief=tk.SOLID,
            bd=1
        ).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Max message length
        msg_len_frame = tk.Frame(inner, bg=COLORS['background'])
        msg_len_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(
            msg_len_frame,
            text="Longueur max message:",
            width=20,
            font=FONTS['body'],
            fg=COLORS['text_primary'],
            bg=COLORS['background'],
            anchor=tk.W
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.msg_len_var = tk.StringVar(
            value=str(self.config.get('ui', 'message_max_length'))
        )
        tk.Entry(
            msg_len_frame,
            textvariable=self.msg_len_var,
            font=FONTS['body'],
            bg=COLORS['background'],
            fg=COLORS['text_primary'],
            relief=tk.SOLID,
            bd=1
        ).pack(side=tk.LEFT, fill=tk.X, expand=True)
    
    def _create_storage_settings(self, parent):
        """Create storage settings."""
        inner = tk.Frame(parent, bg=COLORS['background'], padx=15, pady=15)
        inner.pack(fill=tk.BOTH, expand=True)
        
        # Database location
        db_frame = tk.Frame(inner, bg=COLORS['background'])
        db_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(
            db_frame,
            text="Emplacement BD:",
            font=FONTS['body'],
            fg=COLORS['text_primary'],
            bg=COLORS['background'],
            anchor=tk.W
        ).pack(fill=tk.X, pady=(0, 5))
        
        db_path_label = tk.Label(
            db_frame,
            text=self.config.get('storage', 'database_path'),
            font=FONTS['small'],
            fg=COLORS['text_secondary'],
            bg=COLORS['secondary'],
            anchor=tk.W,
            padx=10,
            pady=5,
            relief=tk.FLAT
        )
        db_path_label.pack(fill=tk.X)
        
        # Export button
        export_btn = tk.Button(
            inner,
            text="Exporter les données",
            font=FONTS['body'],
            bg=COLORS['secondary'],
            fg=COLORS['text_primary'],
            relief=tk.FLAT,
            bd=0,
            padx=15,
            pady=8,
            cursor='hand2',
            command=self._export_data
        )
        export_btn.pack(pady=(10, 0))
        
        # Clear data button
        clear_btn = tk.Button(
            inner,
            text="⚠️ Nettoyer les données",
            font=FONTS['body'],
            bg=COLORS['danger'],
            fg='white',
            relief=tk.FLAT,
            bd=0,
            padx=15,
            pady=8,
            cursor='hand2',
            command=self._clear_data
        )
        clear_btn.pack(pady=(5, 0))
        
        # Info
        info_label = tk.Label(
            inner,
            text="Note: La suppression des données est irréversible.",
            font=FONTS['small'],
            fg=COLORS['text_secondary'],
            bg=COLORS['background'],
            wraplength=450,
            justify=tk.LEFT
        )
        info_label.pack(pady=(20, 0), anchor=tk.W)
    
    def _export_data(self):
        """Export conversation data."""
        messagebox.showinfo(
            "Export",
            "Fonctionnalité à implémenter:\nExport des conversations et historique."
        )
    
    def _clear_data(self):
        """Clear all stored data."""
        result = messagebox.askyesnocancel(
            "Nettoyer les données",
            "⚠️ ATTENTION ⚠️\n\n"
            "Cela supprimera TOUTES les conversations et l'historique.\n"
            "Cette action est irréversible.\n\n"
            "Êtes-vous sûr de vouloir continuer?"
        )
        if result:
            messagebox.showinfo(
                "Non implémenté",
                "Fonctionnalité à implémenter:\nSuppression de toutes les données."
            )
    
    def _save_settings(self):
        """Save settings and close window."""
        try:
            # Validate and update network settings
            self.config._config['network']['default_port'] = int(self.port_var.get())
            self.config._config['network']['connection_timeout'] = int(self.timeout_var.get())
            self.config._config['network']['heartbeat_interval'] = int(self.heartbeat_var.get())
            
            # Validate and update security settings
            self.config._config['security']['rekeying_message_threshold'] = int(self.rekey_msg_var.get())
            self.config._config['security']['rekeying_time_threshold'] = int(self.rekey_time_var.get())
            
            # Validate and update UI settings
            self.config._config['ui']['window_width'] = int(self.width_var.get())
            self.config._config['ui']['window_height'] = int(self.height_var.get())
            self.config._config['ui']['message_max_length'] = int(self.msg_len_var.get())
            
            # Save to file
            self.config.save()
            
            messagebox.showinfo("Paramètres enregistrés", "Les paramètres ont été enregistrés avec succès.")
            self.window.destroy()
            
        except ValueError as e:
            messagebox.showerror("Entrée invalide", "Veuillez entrer des valeurs numériques valides.")
