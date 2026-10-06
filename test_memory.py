from db import (
    save_memory,
    get_memory,
    get_all_memories
)


# Save a memory
save_memory(
    "favorite_language",
    "C++"
)

print("Memory saved successfully!")


# Retrieve one memory
memory = get_memory(
    "favorite_language"
)

print("\nRetrieved memory:")
print(memory)


# Retrieve all memories
memories = get_all_memories()

print("\nAll memories:")

for key, value in memories:
    print(key, ":", value)