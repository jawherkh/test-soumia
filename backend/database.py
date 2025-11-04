import sqlite3
import pickle
import os
import uuid
from datetime import datetime

DB_PATH = "data/chat_history.db"

def init_db():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='messages'")
    messages_exists = cursor.fetchone() is not None
    
    if messages_exists:
        cursor.execute("PRAGMA table_info(messages)")
        columns = [row[1] for row in cursor.fetchall()]
        
        if 'conversation_id' not in columns:
            cursor.execute("DROP TABLE IF EXISTS messages")
            messages_exists = False
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id TEXT PRIMARY KEY,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    
    if not messages_exists:
        cursor.execute("""
            CREATE TABLE messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                image BLOB,
                pdf BLOB,
                filename TEXT,
                FOREIGN KEY (conversation_id) REFERENCES conversations(id)
            )
        """)
    
    conn.commit()
    conn.close()

def create_conversation():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    conversation_id = str(uuid.uuid4())
    now = datetime.now().isoformat()
    
    cursor.execute("""
        INSERT INTO conversations (id, created_at, updated_at)
        VALUES (?, ?, ?)
    """, (conversation_id, now, now))
    
    conn.commit()
    conn.close()
    
    return conversation_id

def update_conversation_timestamp(conversation_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        UPDATE conversations SET updated_at = ? WHERE id = ?
    """, (datetime.now().isoformat(), conversation_id))
    
    conn.commit()
    conn.close()

def save_message(conversation_id, role, content, image=None, pdf=None, filename=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    image_blob = pickle.dumps(image) if image else None
    pdf_blob = pickle.dumps(pdf) if pdf else None
    
    cursor.execute("""
        INSERT INTO messages (conversation_id, timestamp, role, content, image, pdf, filename)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (conversation_id, datetime.now().isoformat(), role, content, image_blob, pdf_blob, filename))
    
    conn.commit()
    conn.close()
    
    update_conversation_timestamp(conversation_id)

def load_conversations():
    if not os.path.exists(DB_PATH):
        return []
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, created_at, updated_at FROM conversations ORDER BY updated_at DESC")
    rows = cursor.fetchall()
    conn.close()
    
    conversations = []
    for row in rows:
        conversations.append({
            "id": row[0],
            "created_at": row[1],
            "updated_at": row[2]
        })
    
    return conversations

def load_conversation_messages(conversation_id):
    if not os.path.exists(DB_PATH):
        return []
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT role, content, image, pdf, filename 
        FROM messages 
        WHERE conversation_id = ? 
        ORDER BY id
    """, (conversation_id,))
    rows = cursor.fetchall()
    conn.close()
    
    messages = []
    for row in rows:
        role, content, image_blob, pdf_blob, filename = row
        msg = {
            "role": role,
            "content": content
        }
        if image_blob:
            msg["image"] = pickle.loads(image_blob)
        if pdf_blob:
            msg["pdf"] = pickle.loads(pdf_blob)
            msg["filename"] = filename
        messages.append(msg)
    
    return messages

def delete_conversation(conversation_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM messages WHERE conversation_id = ?", (conversation_id,))
    cursor.execute("DELETE FROM conversations WHERE id = ?", (conversation_id,))
    
    conn.commit()
    conn.close()

def clear_all_history():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    init_db()
