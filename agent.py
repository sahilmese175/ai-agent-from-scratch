import requests
import json

from tool_registry import TOOLS

from db import (
    create_conversation,
    save_message,
    get_messages,
    get_all_memories,
    save_memory
)


# =========================================
# TOOL DESCRIPTIONS
# =========================================

def get_tool_descriptions():

    descriptions = ""

    for name, tool in TOOLS.items():

        descriptions += f"""
Tool: {name}
Description: {tool["description"]}
Arguments: {tool["arguments"]}
"""

    return descriptions


# =========================================
# EXECUTE TOOL
# =========================================

def execute_tool(tool_name, arguments):

    if tool_name not in TOOLS:
        return "Tool not found"

    tool = TOOLS[tool_name]

    return tool["function"](**arguments)


# =========================================
# PARSE LLM RESPONSE
# =========================================

def parse_llm_response(response):

    response = response.strip()

    if response.startswith("```json"):
        response = response[7:]

    if response.startswith("```"):
        response = response[3:]

    if response.endswith("```"):
        response = response[:-3]

    response = response.strip()

    try:
        return json.loads(response)

    except json.JSONDecodeError:
        return None


# =========================================
# ASK QWEN
# =========================================

def ask_llm(prompt):

    url = "http://localhost:11434/api/generate"

    data = {
        "model": "qwen3:4b",
        "prompt": prompt,
        "stream": False
    }

    response = requests.post(
        url,
        json=data
    )

    return response.json()["response"]


# =========================================
# LOAD LONG-TERM MEMORY
# =========================================

def load_memories():

    memories = get_all_memories()

    if not memories:
        return "No long-term memories stored."

    memory_text = ""

    for key, value in memories:

        memory_text += (
            f"- {key}: {value}\n"
        )

    return memory_text


# =========================================
# USER INPUT
# =========================================

user_input = input("You: ")


# =========================================
# TOOL DESCRIPTIONS
# =========================================

tool_descriptions = get_tool_descriptions()


# =========================================
# CONVERSATION MANAGEMENT
# =========================================

conversation_input = input(
    "\nEnter conversation ID "
    "(press Enter for new conversation): "
)


if conversation_input.strip() == "":

    conversation_id = create_conversation(
        "AI Agent Conversation"
    )

    print(
        f"\nCreated new conversation: "
        f"{conversation_id}"
    )

else:

    conversation_id = int(
        conversation_input
    )

    print(
        f"\nContinuing conversation: "
        f"{conversation_id}"
    )


# =========================================
# LOAD CONVERSATION HISTORY
# =========================================

history = []

previous_messages = get_messages(
    conversation_id
)

for role, content in previous_messages:

    history.append(
        f"{role}: {content}"
    )


# =========================================
# LOAD LONG-TERM MEMORY
# =========================================

memory_text = load_memories()


# =========================================
# SAVE USER MESSAGE
# =========================================

save_message(
    conversation_id,
    "user",
    user_input
)

history.append(
    f"user: {user_input}"
)


# =========================================
# INITIAL PROMPT
# =========================================

prompt = f"""
You are an AI agent.

You have access to these tools:

{tool_descriptions}

You also have long-term memory.

Current long-term memory:

{memory_text}

Important memory rule:

Only create a memory when the user gives a useful,
stable personal fact, preference, identity detail,
or important information that should be remembered
across future conversations.

Do NOT create memories for ordinary questions,
temporary requests, calculations, or tool results.

If you decide something should be remembered,
include:

"memory": {{
    "key": "short_key",
    "value": "information to remember"
}}

Otherwise use:

"memory": null

If you need a tool, return ONLY valid JSON:

{{
    "tool": "tool_name",
    "arguments": {{
        "argument_name": "value"
    }},
    "memory": null
}}

If you have enough information to answer:

{{
    "tool": "none",
    "answer": "your final answer",
    "memory": null
}}

Conversation history:

{history}

User request:

{user_input}
"""


# =========================================
# AGENT LOOP
# =========================================

while True:

    # -------------------------------------
    # Ask Qwen
    # -------------------------------------

    response = ask_llm(prompt)

    print("\nLLM response:")
    print(response)


    # -------------------------------------
    # Parse response
    # -------------------------------------

    data = parse_llm_response(
        response
    )

    if data is None:

        print(
            "\nInvalid JSON returned by LLM."
        )

        print(
            "Agent stopped safely."
        )

        break


    # -------------------------------------
    # Save memory if provided
    # -------------------------------------

    memory = data.get("memory")

    if isinstance(memory, dict):

        memory_key = memory.get("key")
        memory_value = memory.get("value")

        if memory_key and memory_value:

            save_memory(
                memory_key,
                memory_value
            )

            print(
                f"\nMemory saved: "
                f"{memory_key} = {memory_value}"
            )


    # -------------------------------------
    # Add agent response to history
    # -------------------------------------

    history.append(
        f"Agent: {response}"
    )


    # -------------------------------------
    # Get tool
    # -------------------------------------

    tool_name = data.get(
        "tool"
    )


    # =====================================
    # FINAL ANSWER
    # =====================================

    if tool_name == "none":

        final_answer = data.get(
            "answer",
            "Done."
        )

        print("\nFinal answer:")
        print(final_answer)

        save_message(
            conversation_id,
            "assistant",
            final_answer
        )

        break


    # =====================================
    # CHECK TOOL
    # =====================================

    if tool_name not in TOOLS:

        print(
            "\nUnknown tool:",
            tool_name
        )

        break


    # =====================================
    # TOOL ARGUMENTS
    # =====================================

    arguments = data.get(
        "arguments",
        {}
    )


    # =====================================
    # EXECUTE TOOL
    # =====================================

    result = execute_tool(
        tool_name,
        arguments
    )

    print("\nTool result:")
    print(result)


    # =====================================
    # SAVE TOOL RESULT
    # =====================================

    history.append(
        f"Tool {tool_name} result: {result}"
    )

    save_message(
        conversation_id,
        "tool",
        f"{tool_name}: {result}"
    )


    # =====================================
    # REFRESH MEMORY
    # =====================================

    memory_text = load_memories()


    # =====================================
    # NEXT PROMPT
    # =====================================

    prompt = f"""
You are an AI agent.

Available tools:

{tool_descriptions}

Long-term memory:

{memory_text}

Original user request:

{user_input}

Conversation history:

{history}

Decide what to do next.

If you need another tool, return ONLY valid JSON:

{{
    "tool": "tool_name",
    "arguments": {{
        "argument_name": "value"
    }},
    "memory": null
}}

If you have enough information:

{{
    "tool": "none",
    "answer": "your final answer",
    "memory": null
}}
"""