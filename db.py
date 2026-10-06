import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()


# =========================================
# MySQL Connection
# =========================================

def get_connection():

    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )


# =========================================
# Conversations
# =========================================

def create_conversation(title):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO conversations (title)
        VALUES (%s)
        """,
        (title,)
    )

    connection.commit()

    conversation_id = cursor.lastrowid

    cursor.close()
    connection.close()

    return conversation_id


def save_message(conversation_id, role, content):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO messages
        (conversation_id, role, content)
        VALUES (%s, %s, %s)
        """,
        (conversation_id, role, content)
    )

    connection.commit()

    cursor.close()
    connection.close()


def get_messages(conversation_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT role, content
        FROM messages
        WHERE conversation_id = %s
        ORDER BY id ASC
        """,
        (conversation_id,)
    )

    messages = cursor.fetchall()

    cursor.close()
    connection.close()

    return messages


# =========================================
# Long-Term Memory
# =========================================

def save_memory(memory_key, memory_value):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT id
        FROM memories
        WHERE memory_key = %s
        """,
        (memory_key,)
    )

    existing = cursor.fetchone()

    if existing:

        cursor.execute(
            """
            UPDATE memories
            SET memory_value = %s
            WHERE memory_key = %s
            """,
            (memory_value, memory_key)
        )

    else:

        cursor.execute(
            """
            INSERT INTO memories
            (memory_key, memory_value)
            VALUES (%s, %s)
            """,
            (memory_key, memory_value)
        )

    connection.commit()

    cursor.close()
    connection.close()


def get_memory(memory_key):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT memory_value
        FROM memories
        WHERE memory_key = %s
        """,
        (memory_key,)
    )

    result = cursor.fetchone()

    cursor.close()
    connection.close()

    if result:
        return result[0]

    return None


def get_all_memories():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT memory_key, memory_value
        FROM memories
        ORDER BY id ASC
        """
    )

    memories = cursor.fetchall()

    cursor.close()
    connection.close()

    return memories