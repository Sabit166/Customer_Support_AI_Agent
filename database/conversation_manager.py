# src/database/conversation_manager.py
import mysql.connector
from mysql.connector import Error
import json
from datetime import datetime
from typing import List, Dict, Optional
import uuid
import os
from dotenv import load_dotenv

load_dotenv()

class ConversationManager:
    def __init__(self, 
                 host: str = None,
                 database: str = None,
                 user: str = None,
                 password: str = None,
                 port: int = 3306):
        """
        Initialize MySQL connection
        Can use parameters or environment variables
        """
        self.config = {
            'host': host or os.getenv('MYSQL_HOST', 'localhost'),
            'database': database or os.getenv('MYSQL_DATABASE', 'customer_support'),
            'user': user or os.getenv('MYSQL_USER', 'root'),
            'password': password or os.getenv('MYSQL_PASSWORD', ''),
            'port': port or int(os.getenv('MYSQL_PORT', 3306)),
            'charset': 'utf8mb4',
            'collation': 'utf8mb4_unicode_ci',
            'autocommit': True
        }
        self.init_database()
    
    def get_connection(self):
        """Create and return a MySQL connection"""
        try:
            connection = mysql.connector.connect(**self.config)
            return connection
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            raise
    
    def init_database(self):
        """Initialize database tables"""
        connection = None
        cursor = None
        
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            
            # Create conversations table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversations (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    customer_id VARCHAR(50) NOT NULL,
                    session_id VARCHAR(100) UNIQUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    status VARCHAR(20) DEFAULT 'active',
                    INDEX idx_customer_id (customer_id),
                    INDEX idx_session_id (session_id),
                    INDEX idx_created_at (created_at)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            ''')
            
            # Create messages table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    conversation_id INT,
                    message_type VARCHAR(10) NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata JSON,
                    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE,
                    INDEX idx_conversation_id (conversation_id),
                    INDEX idx_timestamp (timestamp),
                    INDEX idx_message_type (message_type)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            ''')
            
            # Create customer_context table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS customer_context (
                    customer_id VARCHAR(50) PRIMARY KEY,
                    name VARCHAR(100),
                    email VARCHAR(100),
                    phone VARCHAR(20),
                    preferred_language VARCHAR(10) DEFAULT 'en',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_email (email),
                    INDEX idx_phone (phone)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            ''')
            
            connection.commit()
            print("✅ Database tables initialized successfully")
            
        except Error as e:
            print(f"❌ Error initializing database: {e}")
            if connection:
                connection.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()
    
    def start_conversation(self, customer_id: str) -> str:
        """Start a new conversation for a customer"""
        session_id = f"{customer_id}_{uuid.uuid4().hex[:8]}_{int(datetime.now().timestamp())}"
        
        connection = None
        cursor = None
        
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            
            cursor.execute('''
                INSERT INTO conversations (customer_id, session_id)
                VALUES (%s, %s)
            ''', (customer_id, session_id))
            
            connection.commit()
            print(f"✅ Started new conversation: {session_id}")
            return session_id
            
        except Error as e:
            print(f"❌ Error starting conversation: {e}")
            if connection:
                connection.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()
    
    def add_message(self, session_id: str, message_type: str, content: str, metadata: Dict = None):
        """Add a message to the conversation"""
        connection = None
        cursor = None
        
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            
            # Get conversation ID
            cursor.execute('''
                SELECT id FROM conversations WHERE session_id = %s
            ''', (session_id,))
            
            result = cursor.fetchone()
            if not result:
                raise ValueError(f"Conversation {session_id} not found")
            
            conversation_id = result[0]
            
            # Add message
            metadata_json = json.dumps(metadata) if metadata else None
            cursor.execute('''
                INSERT INTO messages (conversation_id, message_type, content, metadata)
                VALUES (%s, %s, %s, %s)
            ''', (conversation_id, message_type, content, metadata_json))
            
            # Update conversation timestamp (will auto-update due to ON UPDATE CURRENT_TIMESTAMP)
            cursor.execute('''
                UPDATE conversations SET updated_at = CURRENT_TIMESTAMP 
                WHERE session_id = %s
            ''', (session_id,))
            
            connection.commit()
            print(f"✅ Added {message_type} message to conversation {session_id}")
            
        except Error as e:
            print(f"❌ Error adding message: {e}")
            if connection:
                connection.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()
    
    def get_conversation_history(self, session_id: str) -> List[Dict]:
        """Get all messages for a conversation"""
        connection = None
        cursor = None
        
        try:
            connection = self.get_connection()
            cursor = connection.cursor(dictionary=True)  # Return results as dictionaries
            
            cursor.execute('''
                SELECT m.message_type, m.content, m.timestamp, m.metadata
                FROM messages m
                JOIN conversations c ON m.conversation_id = c.id
                WHERE c.session_id = %s
                ORDER BY m.timestamp
            ''', (session_id,))
            
            messages = []
            for row in cursor.fetchall():
                messages.append({
                    'type': row['message_type'],
                    'content': row['content'],
                    'timestamp': row['timestamp'].isoformat() if row['timestamp'] else None,
                    'metadata': json.loads(row['metadata']) if row['metadata'] else None
                })
            
            return messages
            
        except Error as e:
            print(f"❌ Error getting conversation history: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()
    
    def get_customer_conversations(self, customer_id: str, limit: int = 10) -> List[Dict]:
        """Get all conversations for a customer"""
        connection = None
        cursor = None
        
        try:
            connection = self.get_connection()
            cursor = connection.cursor(dictionary=True)
            
            cursor.execute('''
                SELECT c.session_id, c.created_at, c.updated_at, c.status,
                       (SELECT COUNT(*) FROM messages m WHERE m.conversation_id = c.id) as message_count
                FROM conversations c
                WHERE c.customer_id = %s
                ORDER BY c.updated_at DESC
                LIMIT %s
            ''', (customer_id, limit))
            
            conversations = []
            for row in cursor.fetchall():
                conversations.append({
                    'session_id': row['session_id'],
                    'created_at': row['created_at'].isoformat() if row['created_at'] else None,
                    'updated_at': row['updated_at'].isoformat() if row['updated_at'] else None,
                    'status': row['status'],
                    'message_count': row['message_count']
                })
            
            return conversations
            
        except Error as e:
            print(f"❌ Error getting customer conversations: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()
    
    def update_customer_context(self, customer_id: str, name: str = None, 
                              email: str = None, phone: str = None):
        """Update customer information"""
        connection = None
        cursor = None
        
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            
            cursor.execute('''
                INSERT INTO customer_context (customer_id, name, email, phone)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                name = COALESCE(VALUES(name), name),
                email = COALESCE(VALUES(email), email),
                phone = COALESCE(VALUES(phone), phone)
            ''', (customer_id, name, email, phone))
            
            connection.commit()
            print(f"✅ Updated customer context for {customer_id}")
            
        except Error as e:
            print(f"❌ Error updating customer context: {e}")
            if connection:
                connection.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()
    
    def search_conversations(self, customer_id: str, query: str) -> List[Dict]:
        """Search through customer's conversation history"""
        connection = None
        cursor = None
        
        try:
            connection = self.get_connection()
            cursor = connection.cursor(dictionary=True)
            
            cursor.execute('''
                SELECT c.session_id, m.content, m.timestamp, m.message_type
                FROM messages m
                JOIN conversations c ON m.conversation_id = c.id
                WHERE c.customer_id = %s AND m.content LIKE %s
                ORDER BY m.timestamp DESC
                LIMIT 50
            ''', (customer_id, f'%{query}%'))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'session_id': row['session_id'],
                    'content': row['content'],
                    'timestamp': row['timestamp'].isoformat() if row['timestamp'] else None,
                    'message_type': row['message_type']
                })
            
            return results
            
        except Error as e:
            print(f"❌ Error searching conversations: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()
    
    def get_customer_analytics(self, customer_id: str) -> Dict:
        """Get analytics for a customer"""
        connection = None
        cursor = None
        
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            
            cursor.execute('''
                SELECT 
                    COUNT(*) as total_conversations,
                    SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) as active_conversations,
                    MIN(created_at) as first_interaction,
                    MAX(updated_at) as last_interaction
                FROM conversations 
                WHERE customer_id = %s
            ''', (customer_id,))
            
            result = cursor.fetchone()
            
            return {
                'total_conversations': result[0] if result else 0,
                'active_conversations': result[1] if result else 0,
                'first_interaction': result[2].isoformat() if result and result[2] else None,
                'last_interaction': result[3].isoformat() if result and result[3] else None
            }
            
        except Error as e:
            print(f"❌ Error getting customer analytics: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()
    
    def close_conversation(self, session_id: str):
        """Mark a conversation as closed"""
        connection = None
        cursor = None
        
        try:
            connection = self.get_connection()
            cursor = connection.cursor()
            
            cursor.execute('''
                UPDATE conversations 
                SET status = 'closed', updated_at = CURRENT_TIMESTAMP
                WHERE session_id = %s
            ''', (session_id,))
            
            connection.commit()
            print(f"✅ Closed conversation {session_id}")
            
        except Error as e:
            print(f"❌ Error closing conversation: {e}")
            if connection:
                connection.rollback()
            raise
        finally:
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()

# Usage example and testing
if __name__ == "__main__":
    # Test the conversation manager
    try:
        conv_manager = ConversationManager()
        
        # Test basic functionality
        session_id = conv_manager.start_conversation("CUST-12345")
        conv_manager.add_message(session_id, "user", "Hello, I need help with my internet")
        conv_manager.add_message(session_id, "assistant", "I'd be happy to help you with your internet issue.")
        
        # Get conversation history
        history = conv_manager.get_conversation_history(session_id)
        print(f"Conversation history: {history}")
        
        # Get customer conversations
        conversations = conv_manager.get_customer_conversations("CUST-12345")
        print(f"Customer conversations: {conversations}")
        
    except Exception as e:
        print(f"Test failed: {e}")