import mysql.connector


# =========================================
# MySQL Connection
# =========================================

def get_connection():

    connection = mysql.connector.connect(
        host="localhost",
        user="agent_user",
        password="Sahil@1234",
        database="ai_agent_db"
    )

    return connection


# =========================================
# Conversation Functions
# =========================================

def create_conversation(title):

    connection = get_connection()
    cursor = connection.cursor()

    query = """
    INSERT INTO conversations (title)
    VALUES (%s)
    """

    cursor.execute(query, (title,))

    connection.commit()

    conversation_id = cursor.lastrowid

    cursor.close()
    connection.close()

    return conversation_id


def save_message(conversation_id, role, content):

    connection = get_connection()
    cursor = connection.cursor()

    query = """
    INSERT INTO messages
    (conversation_id, role, content)
    VALUES (%s, %s, %s)
    """

    cursor.execute(
        query,
        (conversation_id, role, content)
    )

    connection.commit()

    cursor.close()
    connection.close()


def get_messages(conversation_id):

    connection = get_connection()
    cursor = connection.cursor()

    query = """
    SELECT role, content
    FROM messages
    WHERE conversation_id = %s
    ORDER BY id ASC
    """

    cursor.execute(
        query,
        (conversation_id,)
    )

    messages = cursor.fetchall()

    cursor.close()
    connection.close()

    return messages


# =========================================
# Long-Term Memory Functions
# =========================================

def save_memory(memory_key, memory_value):

    connection = get_connection()
    cursor = connection.cursor()

    # Check whether this memory already exists
    check_query = """
    SELECT id
    FROM memories
    WHERE memory_key = %s
    """

    cursor.execute(
        check_query,
        (memory_key,)
    )

    existing_memory = cursor.fetchone()


    if existing_memory:

        # Update existing memory
        update_query = """
        UPDATE memories
        SET memory_value = %s
        WHERE memory_key = %s
        """

        cursor.execute(
            update_query,
            (memory_value, memory_key)
        )

    else:

        # Create new memory
        insert_query = """
        INSERT INTO memories
        (memory_key, memory_value)
        VALUES (%s, %s)
        """

        cursor.execute(
            insert_query,
            (memory_key, memory_value)
        )


    connection.commit()

    cursor.close()
    connection.close()


def get_memory(memory_key):

    connection = get_connection()
    cursor = connection.cursor()

    query = """
    SELECT memory_value
    FROM memories
    WHERE memory_key = %s
    """

    cursor.execute(
        query,
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

    query = """
    SELECT memory_key, memory_value
    FROM memories
    ORDER BY id ASC
    """

    cursor.execute(query)

    memories = cursor.fetchall()

    cursor.close()
    connection.close()

    return memories