"""
Conversation storage manager.
High-level interface for managing conversations and messages.
"""

from storage.database_manager import DatabaseManager
from utils.logger import SecureLogger

logger = SecureLogger('conversation_storage')


class ConversationStorage:
    """Manages conversation storage and retrieval."""
    
    def __init__(self, db_manager):
        """
        Initialize conversation storage.
        
        Args:
            db_manager: DatabaseManager instance
        """
        self.db = db_manager
        self.current_conversation_id = None
    
    def start_conversation(self, peer_fingerprint, peer_name=None):
        """
        Start or resume a conversation.
        
        Args:
            peer_fingerprint: Peer's fingerprint
            peer_name: Optional peer display name
            
        Returns:
            int: Conversation ID
        """
        conversation_id = self.db.create_conversation(peer_fingerprint, peer_name)
        self.current_conversation_id = conversation_id
        logger.info(f"Started conversation {conversation_id}", event="conversation")
        return conversation_id
    
    def save_sent_message(self, content, message_type='text'):
        """
        Save a sent message.
        
        Args:
            content: Message content
            message_type: 'text' or 'file'
            
        Returns:
            int: Message ID
        """
        if not self.current_conversation_id:
            raise ValueError("No active conversation")
        
        return self.db.save_message(
            self.current_conversation_id,
            'sent',
            content,
            message_type
        )
    
    def save_received_message(self, content, message_type='text'):
        """
        Save a received message.
        
        Args:
            content: Message content
            message_type: 'text' or 'file'
            
        Returns:
            int: Message ID
        """
        if not self.current_conversation_id:
            raise ValueError("No active conversation")
        
        return self.db.save_message(
            self.current_conversation_id,
            'received',
            content,
            message_type
        )
    
    def get_conversation_messages(self, conversation_id=None, limit=100):
        """
        Get messages for a conversation.
        
        Args:
            conversation_id: Conversation ID (uses current if None)
            limit: Maximum number of messages
            
        Returns:
            list: List of messages
        """
        conv_id = conversation_id or self.current_conversation_id
        if not conv_id:
            return []
        
        return self.db.get_messages(conv_id, limit)
    
    def get_all_conversations(self):
        """
        Get all conversations.
        
        Returns:
            list: List of conversations
        """
        return self.db.get_conversations()
    
    def set_current_conversation(self, conversation_id):
        """
        Set the current active conversation.
        
        Args:
            conversation_id: Conversation ID
        """
        self.current_conversation_id = conversation_id
