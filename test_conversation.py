from db import create_conversation, save_message, get_messages


# Create a conversation
conversation_id = create_conversation(
    "Test Conversation"
)

print("Created conversation:", conversation_id)


# Save messages
save_message(
    conversation_id,
    "user",
    "My favorite language is C++"
)

save_message(
    conversation_id,
    "assistant",
    "Got it!"
)


# Retrieve messages
messages = get_messages(conversation_id)

print("\nRetrieved messages:")

for role, content in messages:
    print(role, ":", content)