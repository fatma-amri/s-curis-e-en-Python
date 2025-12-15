"""
Custom widgets for the messenger GUI.
"""

import tkinter as tk
from tkinter import ttk
from gui.styles import COLORS, FONTS, ICONS


class MessageBubble(tk.Frame):
    """Custom message bubble widget."""
    
    def __init__(self, parent, text, direction='sent', timestamp='', **kwargs):
        """
        Initialize message bubble.
        
        Args:
            parent: Parent widget
            text: Message text
            direction: 'sent' or 'received'
            timestamp: Timestamp string
        """
        super().__init__(parent, bg=COLORS['background'], **kwargs)
        
        self.text = text
        self.direction = direction
        self.timestamp = timestamp
        
        self._create_bubble()
    
    def _create_bubble(self):
        """Create the bubble components."""
        # Container for alignment
        container = tk.Frame(self, bg=COLORS['background'])
        container.pack(fill=tk.X, pady=3)
        
        if self.direction == 'sent':
            # Sent message - right aligned, blue
            bubble_color = COLORS['bubble_sent']
            text_color = 'white'
            anchor = tk.E
            side = tk.RIGHT
        else:
            # Received message - left aligned, gray
            bubble_color = COLORS['bubble_received']
            text_color = COLORS['text_primary']
            anchor = tk.W
            side = tk.LEFT
        
        # Bubble frame with rounded appearance
        bubble = tk.Frame(container, bg=bubble_color, bd=0, relief=tk.FLAT)
        bubble.pack(side=side, padx=10)
        
        # Message text
        text_label = tk.Label(
            bubble,
            text=self.text,
            bg=bubble_color,
            fg=text_color,
            font=FONTS['body'],
            wraplength=350,
            justify=tk.LEFT,
            padx=12,
            pady=8
        )
        text_label.pack()
        
        # Timestamp below bubble
        if self.timestamp:
            time_label = tk.Label(
                container,
                text=self.timestamp,
                font=FONTS['tiny'],
                fg=COLORS['text_secondary'],
                bg=COLORS['background']
            )
            time_label.pack(side=side, padx=15, pady=(2, 0))


class ConversationCard(tk.Frame):
    """Custom conversation card widget for the sidebar."""
    
    def __init__(self, parent, contact_name, last_message='', timestamp='', 
                 unread_count=0, is_online=False, **kwargs):
        """
        Initialize conversation card.
        
        Args:
            parent: Parent widget
            contact_name: Name of the contact
            last_message: Preview of last message
            timestamp: Timestamp string
            unread_count: Number of unread messages
            is_online: Whether contact is online
        """
        super().__init__(parent, bg=COLORS['sidebar'], **kwargs)
        
        self.contact_name = contact_name
        self.last_message = last_message
        self.timestamp = timestamp
        self.unread_count = unread_count
        self.is_online = is_online
        self.selected = False
        
        self._create_card()
        
        # Make clickable
        self.bind('<Button-1>', self._on_click)
        for child in self.winfo_children():
            child.bind('<Button-1>', self._on_click)
    
    def _create_card(self):
        """Create the card components."""
        self.config(relief=tk.FLAT, bd=1, highlightthickness=1,
                   highlightbackground=COLORS['border'])
        
        # Padding frame
        padding_frame = tk.Frame(self, bg=COLORS['sidebar'])
        padding_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)
        
        # Top row - name and timestamp
        top_row = tk.Frame(padding_frame, bg=COLORS['sidebar'])
        top_row.pack(fill=tk.X)
        
        # Online indicator + name
        name_frame = tk.Frame(top_row, bg=COLORS['sidebar'])
        name_frame.pack(side=tk.LEFT)
        
        status_icon = ICONS['connected'] if self.is_online else '⚪'
        status_label = tk.Label(
            name_frame,
            text=status_icon,
            font=FONTS['small'],
            bg=COLORS['sidebar']
        )
        status_label.pack(side=tk.LEFT, padx=(0, 5))
        status_label.bind('<Button-1>', self._on_click)
        
        name_label = tk.Label(
            name_frame,
            text=self.contact_name,
            font=FONTS['heading'],
            fg=COLORS['text_primary'],
            bg=COLORS['sidebar']
        )
        name_label.pack(side=tk.LEFT)
        name_label.bind('<Button-1>', self._on_click)
        
        # Timestamp
        if self.timestamp:
            time_label = tk.Label(
                top_row,
                text=self.timestamp,
                font=FONTS['small'],
                fg=COLORS['text_secondary'],
                bg=COLORS['sidebar']
            )
            time_label.pack(side=tk.RIGHT)
            time_label.bind('<Button-1>', self._on_click)
        
        # Bottom row - last message preview
        if self.last_message:
            msg_label = tk.Label(
                padding_frame,
                text=self.last_message[:40] + ('...' if len(self.last_message) > 40 else ''),
                font=FONTS['body'],
                fg=COLORS['text_secondary'],
                bg=COLORS['sidebar'],
                anchor=tk.W,
                justify=tk.LEFT
            )
            msg_label.pack(fill=tk.X, pady=(5, 0))
            msg_label.bind('<Button-1>', self._on_click)
        
        # Unread badge
        if self.unread_count > 0:
            badge = tk.Label(
                padding_frame,
                text=str(self.unread_count),
                font=FONTS['small'],
                fg='white',
                bg=COLORS['primary'],
                padx=6,
                pady=2
            )
            badge.place(relx=1.0, rely=1.0, anchor=tk.SE, x=-5, y=-5)
            badge.bind('<Button-1>', self._on_click)
    
    def _on_click(self, event=None):
        """Handle card click."""
        self.select()
    
    def select(self):
        """Mark this card as selected."""
        self.selected = True
        self.config(bg=COLORS['active'], highlightbackground=COLORS['primary'])
        for child in self.winfo_children():
            if isinstance(child, tk.Frame):
                child.config(bg=COLORS['active'])
                for subchild in child.winfo_children():
                    if isinstance(subchild, (tk.Label, tk.Frame)):
                        subchild.config(bg=COLORS['active'])
    
    def deselect(self):
        """Mark this card as not selected."""
        self.selected = False
        self.config(bg=COLORS['sidebar'], highlightbackground=COLORS['border'])
        for child in self.winfo_children():
            if isinstance(child, tk.Frame):
                child.config(bg=COLORS['sidebar'])
                for subchild in child.winfo_children():
                    if isinstance(subchild, (tk.Label, tk.Frame)):
                        subchild.config(bg=COLORS['sidebar'])


class StatusBar(tk.Frame):
    """Custom status bar widget."""
    
    def __init__(self, parent, **kwargs):
        """
        Initialize status bar.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent, relief=tk.SUNKEN, bd=1, **kwargs)
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create status bar widgets."""
        # Connection status (left)
        self.status_frame = tk.Frame(self, bg=COLORS['background'])
        self.status_frame.pack(side=tk.LEFT, padx=5, pady=2)
        
        self.status_icon = tk.Label(
            self.status_frame,
            text=ICONS['disconnected'],
            font=FONTS['body'],
            bg=COLORS['background']
        )
        self.status_icon.pack(side=tk.LEFT, padx=(0, 5))
        
        self.status_text = tk.Label(
            self.status_frame,
            text='Disconnected',
            font=FONTS['small'],
            bg=COLORS['background']
        )
        self.status_text.pack(side=tk.LEFT)
        
        # Connection info (right)
        self.info_frame = tk.Frame(self, bg=COLORS['background'])
        self.info_frame.pack(side=tk.RIGHT, padx=5, pady=2)
        
        self.ip_label = tk.Label(
            self.info_frame,
            text='IP: Not connected',
            font=FONTS['small'],
            bg=COLORS['background']
        )
        self.ip_label.pack(side=tk.LEFT, padx=5)
        
        self.port_label = tk.Label(
            self.info_frame,
            text='Port: ---',
            font=FONTS['small'],
            bg=COLORS['background']
        )
        self.port_label.pack(side=tk.LEFT, padx=5)
    
    def update_status(self, status, ip='', port=''):
        """
        Update status bar information.
        
        Args:
            status: Status string ('connected', 'disconnected', etc.)
            ip: IP address
            port: Port number
        """
        from gui.styles import get_status_icon, get_status_color
        
        # Update status icon and text
        icon = get_status_icon(status)
        self.status_icon.config(text=icon)
        self.status_text.config(text=status.capitalize())
        
        # Update connection info
        if ip:
            self.ip_label.config(text=f'IP: {ip}')
        else:
            self.ip_label.config(text='IP: Not connected')
        
        if port:
            self.port_label.config(text=f'Port: {port}')
        else:
            self.port_label.config(text='Port: ---')
