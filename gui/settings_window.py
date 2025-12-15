"""
Settings window for the P2P messenger.
"""

import tkinter as tk
from tkinter import ttk, messagebox


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
        self.window.title("Settings")
        self.window.geometry("500x400")
        self.window.resizable(False, False)
        self.window.transient(parent)
        self.window.grab_set()
        
        self._create_widgets()
        
        # Center window
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() // 2) - (500 // 2)
        y = (self.window.winfo_screenheight() // 2) - (400 // 2)
        self.window.geometry(f"500x400+{x}+{y}")
    
    def _create_widgets(self):
        """Create settings widgets."""
        # Main frame
        main_frame = ttk.Frame(self.window, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(
            main_frame,
            text="Application Settings",
            font=('Arial', 14, 'bold')
        )
        title_label.pack(pady=(0, 20))
        
        # Notebook for tabbed settings
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Network settings tab
        network_frame = ttk.Frame(notebook, padding="10")
        notebook.add(network_frame, text="Network")
        self._create_network_settings(network_frame)
        
        # Security settings tab
        security_frame = ttk.Frame(notebook, padding="10")
        notebook.add(security_frame, text="Security")
        self._create_security_settings(security_frame)
        
        # UI settings tab
        ui_frame = ttk.Frame(notebook, padding="10")
        notebook.add(ui_frame, text="Interface")
        self._create_ui_settings(ui_frame)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(
            button_frame,
            text="Cancel",
            command=self.window.destroy
        ).pack(side=tk.RIGHT, padx=(5, 0))
        
        ttk.Button(
            button_frame,
            text="Save",
            command=self._save_settings
        ).pack(side=tk.RIGHT)
    
    def _create_network_settings(self, parent):
        """Create network settings."""
        # Default port
        port_frame = ttk.Frame(parent)
        port_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(port_frame, text="Default Port:", width=20).pack(side=tk.LEFT)
        
        self.port_var = tk.StringVar(
            value=str(self.config.get('network', 'default_port'))
        )
        ttk.Entry(port_frame, textvariable=self.port_var).pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0)
        )
        
        # Connection timeout
        timeout_frame = ttk.Frame(parent)
        timeout_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(timeout_frame, text="Connection Timeout (s):", width=20).pack(side=tk.LEFT)
        
        self.timeout_var = tk.StringVar(
            value=str(self.config.get('network', 'connection_timeout'))
        )
        ttk.Entry(timeout_frame, textvariable=self.timeout_var).pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0)
        )
        
        # Heartbeat interval
        heartbeat_frame = ttk.Frame(parent)
        heartbeat_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(heartbeat_frame, text="Heartbeat Interval (s):", width=20).pack(side=tk.LEFT)
        
        self.heartbeat_var = tk.StringVar(
            value=str(self.config.get('network', 'heartbeat_interval'))
        )
        ttk.Entry(heartbeat_frame, textvariable=self.heartbeat_var).pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0)
        )
    
    def _create_security_settings(self, parent):
        """Create security settings."""
        # Rekeying threshold
        rekey_msg_frame = ttk.Frame(parent)
        rekey_msg_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(rekey_msg_frame, text="Rekey After Messages:", width=20).pack(side=tk.LEFT)
        
        self.rekey_msg_var = tk.StringVar(
            value=str(self.config.get('security', 'rekeying_message_threshold'))
        )
        ttk.Entry(rekey_msg_frame, textvariable=self.rekey_msg_var).pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0)
        )
        
        # Rekeying time threshold
        rekey_time_frame = ttk.Frame(parent)
        rekey_time_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(rekey_time_frame, text="Rekey After Time (s):", width=20).pack(side=tk.LEFT)
        
        self.rekey_time_var = tk.StringVar(
            value=str(self.config.get('security', 'rekeying_time_threshold'))
        )
        ttk.Entry(rekey_time_frame, textvariable=self.rekey_time_var).pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0)
        )
        
        # Info label
        info_label = ttk.Label(
            parent,
            text="Note: Security settings take effect on next connection.",
            font=('Arial', 9, 'italic'),
            foreground='gray'
        )
        info_label.pack(pady=(20, 0))
    
    def _create_ui_settings(self, parent):
        """Create UI settings."""
        # Window dimensions
        width_frame = ttk.Frame(parent)
        width_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(width_frame, text="Window Width:", width=20).pack(side=tk.LEFT)
        
        self.width_var = tk.StringVar(
            value=str(self.config.get('ui', 'window_width'))
        )
        ttk.Entry(width_frame, textvariable=self.width_var).pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0)
        )
        
        height_frame = ttk.Frame(parent)
        height_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(height_frame, text="Window Height:", width=20).pack(side=tk.LEFT)
        
        self.height_var = tk.StringVar(
            value=str(self.config.get('ui', 'window_height'))
        )
        ttk.Entry(height_frame, textvariable=self.height_var).pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0)
        )
        
        # Max message length
        msg_len_frame = ttk.Frame(parent)
        msg_len_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(msg_len_frame, text="Max Message Length:", width=20).pack(side=tk.LEFT)
        
        self.msg_len_var = tk.StringVar(
            value=str(self.config.get('ui', 'message_max_length'))
        )
        ttk.Entry(msg_len_frame, textvariable=self.msg_len_var).pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0)
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
            
            messagebox.showinfo("Settings Saved", "Settings have been saved successfully.")
            self.window.destroy()
            
        except ValueError as e:
            messagebox.showerror("Invalid Input", "Please enter valid numeric values.")
