"""
Connection dialog for the P2P messenger.
Allows user to choose between server and client mode.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from utils.validators import validate_ip, validate_port


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
        self.dialog.title("Connect to Peer")
        self.dialog.geometry("450x350")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self._create_widgets()
        
        # Center dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (450 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (350 // 2)
        self.dialog.geometry(f"450x350+{x}+{y}")
    
    def _create_widgets(self):
        """Create dialog widgets."""
        # Main frame
        main_frame = ttk.Frame(self.dialog, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(
            main_frame,
            text="Establish Secure Connection",
            font=('Arial', 14, 'bold')
        )
        title_label.pack(pady=(0, 20))
        
        # Mode selection
        mode_frame = ttk.LabelFrame(main_frame, text="Connection Mode", padding="10")
        mode_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.mode_var = tk.StringVar(value="listen")
        
        listen_radio = ttk.Radiobutton(
            mode_frame,
            text="Listen (Server Mode) - Wait for incoming connection",
            variable=self.mode_var,
            value="listen",
            command=self._on_mode_change
        )
        listen_radio.pack(anchor=tk.W)
        
        connect_radio = ttk.Radiobutton(
            mode_frame,
            text="Connect (Client Mode) - Connect to peer",
            variable=self.mode_var,
            value="connect",
            command=self._on_mode_change
        )
        connect_radio.pack(anchor=tk.W)
        
        # Connection details
        details_frame = ttk.LabelFrame(main_frame, text="Connection Details", padding="10")
        details_frame.pack(fill=tk.X, pady=(0, 15))
        
        # IP Address (only for client mode)
        ip_frame = ttk.Frame(details_frame)
        ip_frame.pack(fill=tk.X, pady=5)
        
        self.ip_label = ttk.Label(ip_frame, text="Peer IP Address:", width=15)
        self.ip_label.pack(side=tk.LEFT)
        
        self.ip_entry = ttk.Entry(ip_frame)
        self.ip_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        self.ip_entry.insert(0, "127.0.0.1")
        
        # Port
        port_frame = ttk.Frame(details_frame)
        port_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(port_frame, text="Port:", width=15).pack(side=tk.LEFT)
        
        self.port_entry = ttk.Entry(port_frame)
        self.port_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        self.port_entry.insert(0, "5555")
        
        # Fingerprint display
        fp_frame = ttk.LabelFrame(main_frame, text="Your Fingerprint", padding="10")
        fp_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        fingerprint = self.key_manager.get_fingerprint()
        fp_text = tk.Text(fp_frame, height=3, wrap=tk.WORD, font=('Courier', 9))
        fp_text.insert(1.0, fingerprint)
        fp_text.config(state=tk.DISABLED)
        fp_text.pack(fill=tk.BOTH, expand=True)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(
            button_frame,
            text="Cancel",
            command=self._on_cancel
        ).pack(side=tk.RIGHT, padx=(5, 0))
        
        ttk.Button(
            button_frame,
            text="Connect",
            command=self._on_connect
        ).pack(side=tk.RIGHT)
        
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
