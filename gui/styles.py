"""
Centralized styling and theme definitions for the GUI.
"""

# Color palette for the application
COLORS = {
    'primary': '#0084FF',        # Blue principal (messages sent)
    'secondary': '#E4E6EB',      # Gray light (messages received, buttons)
    'success': '#31A24C',        # Green (connected)
    'danger': '#FA3E3E',         # Red (disconnected)
    'warning': '#F7B928',        # Orange (waiting)
    'background': '#FFFFFF',     # White background
    'sidebar': '#F0F2F5',        # Gray sidebar background
    'text_primary': '#050505',   # Primary text
    'text_secondary': '#65676B', # Secondary text
    'border': '#DADDE1',         # Borders
    'bubble_sent': '#0084FF',    # Sent message bubble (blue)
    'bubble_received': '#E4E6EB', # Received message bubble (gray)
    'hover': '#E7F3FF',          # Hover state
    'active': '#D3E3FD',         # Active state
}

# Font configurations
FONTS = {
    'title': ('Arial', 14, 'bold'),
    'heading': ('Arial', 12, 'bold'),
    'body': ('Arial', 10),
    'small': ('Arial', 9),
    'tiny': ('Arial', 8),
    'mono': ('Courier', 9),
    'mono_small': ('Courier', 8),
}

# Widget styling configurations
STYLES = {
    'message_bubble': {
        'padding': (10, 8),
        'wraplength': 350,
        'border_radius': 18,  # Simulated with padding and styling
    },
    'conversation_card': {
        'padding': 10,
        'height': 70,
        'width': 250,
    },
    'status_bar': {
        'height': 30,
        'padding': 5,
    },
    'sidebar': {
        'width': 250,
        'min_width': 200,
    },
    'window': {
        'default_width': 1000,
        'default_height': 700,
        'min_width': 800,
        'min_height': 600,
    },
}

# Icons (Unicode emojis)
ICONS = {
    'connected': '🟢',
    'disconnected': '🔴',
    'waiting': '🟡',
    'search': '🔍',
    'attach': '📎',
    'send': '📤',
    'contact': '👤',
    'lock': '🔒',
    'connect': '🔌',
    'listen': '📡',
    'rocket': '🚀',
    'copy': '📋',
    'check': '✓',
    'double_check': '✓✓',
    'settings': '⚙️',
    'info': 'ℹ️',
}


def get_status_color(status):
    """
    Get color for a given status.
    
    Args:
        status: Status string ('connected', 'disconnected', 'listening', 'connecting')
    
    Returns:
        str: Hex color code
    """
    status_colors = {
        'connected': COLORS['success'],
        'disconnected': COLORS['danger'],
        'listening': COLORS['warning'],
        'connecting': COLORS['warning'],
    }
    return status_colors.get(status.lower(), COLORS['text_secondary'])


def get_status_icon(status):
    """
    Get icon for a given status.
    
    Args:
        status: Status string
    
    Returns:
        str: Unicode icon
    """
    status_icons = {
        'connected': ICONS['connected'],
        'disconnected': ICONS['disconnected'],
        'listening': ICONS['waiting'],
        'connecting': ICONS['waiting'],
    }
    return status_icons.get(status.lower(), '')
