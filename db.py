import mysql.connector


def get_connection():
    connection = mysql.connector.connect(
        host="localhost",
        user="agent_user",
        password="NewPassword123!",
        database="ai_agent_db"
    )

    return connection


def save_message(role, content):
    connection = get_connection()
    cursor = connection.cursor()

    query = """
    INSERT INTO messages (role, content)
    VALUES (%s, %s)
    """

    cursor.execute(query, (role, content))
    connection.commit()

    cursor.close()
    connection.close()


def get_messages():
    connection = get_connection()
    cursor = connection.cursor()

    query = """
    SELECT role, content
    FROM messages
    ORDER BY id ASC
    """

    cursor.execute(query)

    messages = cursor.fetchall()

    cursor.close()
    connection.close()

    return messages