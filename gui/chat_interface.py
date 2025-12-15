"""
Chat interface components for displaying messages.
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime


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
        
        # Chat display area with scrollbar
        display_frame = ttk.Frame(self.container)
        display_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(display_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Canvas for messages (allows better control over message bubbles)
        self.canvas = tk.Canvas(
            display_frame,
            bg='#f0f0f0',
            yscrollcommand=scrollbar.set,
            highlightthickness=0
        )
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar.config(command=self.canvas.yview)
        
        # Frame inside canvas for messages
        self.messages_frame = ttk.Frame(self.canvas)
        self.canvas_window = self.canvas.create_window(
            0, 0,
            window=self.messages_frame,
            anchor=tk.NW
        )
        
        # Bind canvas resize
        self.canvas.bind('<Configure>', self._on_canvas_resize)
        self.messages_frame.bind('<Configure>', self._on_frame_resize)
        
        # Input area
        input_frame = ttk.Frame(self.container)
        input_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Message entry
        self.message_entry = tk.Text(
            input_frame,
            height=3,
            wrap=tk.WORD,
            font=('Arial', 10)
        )
        self.message_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        # Button frame
        button_frame = ttk.Frame(input_frame)
        button_frame.pack(side=tk.RIGHT)
        
        # Send button
        self.send_button = ttk.Button(
            button_frame,
            text="Send",
            state=tk.DISABLED
        )
        self.send_button.pack(pady=(0, 5))
        
        # Attach file button
        self.attach_button = ttk.Button(
            button_frame,
            text="📎 File",
            state=tk.DISABLED
        )
        self.attach_button.pack()
    
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
        
        # Create message frame
        msg_frame = ttk.Frame(self.messages_frame)
        msg_frame.pack(fill=tk.X, pady=5, padx=10)
        
        # Timestamp
        time_str = timestamp.strftime('%H:%M')
        
        if direction == 'sent':
            # Sent message - right aligned, blue
            bubble = tk.Frame(msg_frame, bg='#0084ff', bd=0)
            bubble.pack(side=tk.RIGHT)
            
            text_widget = tk.Label(
                bubble,
                text=text,
                bg='#0084ff',
                fg='white',
                font=('Arial', 10),
                wraplength=300,
                justify=tk.LEFT,
                padx=10,
                pady=8
            )
            text_widget.pack()
            
            time_label = tk.Label(
                msg_frame,
                text=time_str,
                font=('Arial', 8),
                fg='gray'
            )
            time_label.pack(side=tk.RIGHT, padx=(0, 5))
            
        else:
            # Received message - left aligned, gray
            bubble = tk.Frame(msg_frame, bg='#e4e6eb', bd=0)
            bubble.pack(side=tk.LEFT)
            
            text_widget = tk.Label(
                bubble,
                text=text,
                bg='#e4e6eb',
                fg='black',
                font=('Arial', 10),
                wraplength=300,
                justify=tk.LEFT,
                padx=10,
                pady=8
            )
            text_widget.pack()
            
            time_label = tk.Label(
                msg_frame,
                text=time_str,
                font=('Arial', 8),
                fg='gray'
            )
            time_label.pack(side=tk.LEFT, padx=(5, 0))
        
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
