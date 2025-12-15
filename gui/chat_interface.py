"""
Chat interface components for displaying messages.
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime
from gui.styles import COLORS, FONTS, ICONS
from gui.widgets import MessageBubble


class ChatInterface:
    """Chat interface with message bubbles."""
    
    def __init__(self, parent):
        """
        Initialize chat interface.
        
        Args:
            parent: Parent widget
        """
        self.parent = parent
        self.messages = []
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create chat interface widgets."""
        # Main container
        self.container = ttk.Frame(self.parent)
        self.container.pack(fill=tk.BOTH, expand=True)
        
        # Chat header (contact info)
        header_frame = tk.Frame(self.container, bg=COLORS['background'], 
                               relief=tk.SOLID, bd=1)
        header_frame.pack(fill=tk.X, padx=0, pady=0)
        
        header_label = tk.Label(
            header_frame,
            text="Secure P2P Messenger",
            font=FONTS['heading'],
            fg=COLORS['text_primary'],
            bg=COLORS['background'],
            padx=15,
            pady=10
        )
        header_label.pack(side=tk.LEFT)
        
        # Chat display area with scrollbar
        display_frame = tk.Frame(self.container, bg=COLORS['background'])
        display_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(display_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Canvas for messages (allows better control over message bubbles)
        self.canvas = tk.Canvas(
            display_frame,
            bg=COLORS['background'],
            yscrollcommand=scrollbar.set,
            highlightthickness=0
        )
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar.config(command=self.canvas.yview)
        
        # Frame inside canvas for messages
        self.messages_frame = tk.Frame(self.canvas, bg=COLORS['background'])
        self.canvas_window = self.canvas.create_window(
            0, 0,
            window=self.messages_frame,
            anchor=tk.NW
        )
        
        # Bind canvas resize
        self.canvas.bind('<Configure>', self._on_canvas_resize)
        self.messages_frame.bind('<Configure>', self._on_frame_resize)
        
        # Input area with border
        input_container = tk.Frame(self.container, bg=COLORS['border'], bd=1, relief=tk.SOLID)
        input_container.pack(fill=tk.X, padx=0, pady=0)
        
        input_frame = tk.Frame(input_container, bg=COLORS['background'])
        input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Left side - attach button
        left_buttons = tk.Frame(input_frame, bg=COLORS['background'])
        left_buttons.pack(side=tk.LEFT, padx=(0, 5))
        
        self.attach_button = tk.Button(
            left_buttons,
            text=ICONS['attach'],
            font=FONTS['body'],
            state=tk.DISABLED,
            bg=COLORS['background'],
            fg=COLORS['text_secondary'],
            relief=tk.FLAT,
            bd=0,
            padx=8,
            pady=5,
            cursor='hand2'
        )
        self.attach_button.pack()
        
        # Center - message entry
        self.message_entry = tk.Text(
            input_frame,
            height=3,
            wrap=tk.WORD,
            font=FONTS['body'],
            bg=COLORS['background'],
            relief=tk.FLAT,
            bd=0
        )
        self.message_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        # Right side - send button
        right_buttons = tk.Frame(input_frame, bg=COLORS['background'])
        right_buttons.pack(side=tk.RIGHT, padx=(5, 0))
        
        self.send_button = tk.Button(
            right_buttons,
            text=f"Envoyer {ICONS['send']}",
            font=FONTS['body'],
            state=tk.DISABLED,
            bg=COLORS['primary'],
            fg='white',
            relief=tk.FLAT,
            bd=0,
            padx=15,
            pady=8,
            cursor='hand2'
        )
        self.send_button.pack()
    
    def _on_canvas_resize(self, event):
        """Handle canvas resize."""
        self.canvas.itemconfig(self.canvas_window, width=event.width)
    
    def _on_frame_resize(self, event):
        """Handle frame resize."""
        self.canvas.configure(scrollregion=self.canvas.bbox('all'))
        self._scroll_to_bottom()
    
    def _scroll_to_bottom(self):
        """Scroll to bottom of chat."""
        self.canvas.update_idletasks()
        self.canvas.yview_moveto(1.0)
    
    def add_message(self, text, direction='sent', timestamp=None):
        """
        Add a message bubble to the chat.
        
        Args:
            text: Message text
            direction: 'sent' or 'received'
            timestamp: Message timestamp (uses current if None)
        """
        if timestamp is None:
            timestamp = datetime.now()
        elif isinstance(timestamp, str):
            # Parse timestamp string if needed
            try:
                timestamp = datetime.fromisoformat(timestamp)
            except:
                timestamp = datetime.now()
        
        # Format timestamp
        time_str = timestamp.strftime('%H:%M')
        
        # Create message bubble using custom widget
        bubble = MessageBubble(
            self.messages_frame,
            text=text,
            direction=direction,
            timestamp=time_str
        )
        bubble.pack(fill=tk.X, pady=2)
        
        self.messages.append((text, direction, timestamp))
        self._scroll_to_bottom()
    
    def clear_messages(self):
        """Clear all messages from display."""
        for widget in self.messages_frame.winfo_children():
            widget.destroy()
        self.messages.clear()
    
    def get_input_text(self):
        """
        Get text from input field.
        
        Returns:
            str: Input text
        """
        return self.message_entry.get(1.0, tk.END).strip()
    
    def clear_input(self):
        """Clear input field."""
        self.message_entry.delete(1.0, tk.END)
    
    def enable_input(self, enabled=True):
        """
        Enable or disable input controls.
        
        Args:
            enabled: True to enable, False to disable
        """
        state = tk.NORMAL if enabled else tk.DISABLED
        self.send_button.config(state=state)
        self.attach_button.config(state=state)
        self.message_entry.config(state=state)
    
    def set_send_callback(self, callback):
        """
        Set callback for send button.
        
        Args:
            callback: Function to call when send is clicked
        """
        self.send_button.config(command=callback)
    
    def set_attach_callback(self, callback):
        """
        Set callback for attach button.
        
        Args:
            callback: Function to call when attach is clicked
        """
        self.attach_button.config(command=callback)
