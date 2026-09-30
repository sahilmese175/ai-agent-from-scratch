import requests
import json

from tool_registry import TOOLS


# -----------------------------------------
# Get descriptions of all available tools
# -----------------------------------------
def get_tool_descriptions():

    descriptions = ""

    for name, tool in TOOLS.items():

        descriptions += f"""
Tool: {name}
Description: {tool["description"]}
Arguments: {tool["arguments"]}
"""

    return descriptions


# -----------------------------------------
# Execute a tool
# -----------------------------------------
def execute_tool(tool_name, arguments):

    if tool_name not in TOOLS:
        return "Tool not found"

    tool = TOOLS[tool_name]

    function = tool["function"]

    result = function(**arguments)

    return result


# -----------------------------------------
# Send prompt to local Qwen LLM
# -----------------------------------------
def ask_llm(prompt):

    url = "http://localhost:11434/api/generate"

    data = {
        "model": "qwen3:4b",
        "prompt": prompt,
        "stream": False
    }

    response = requests.post(url, json=data)

    return response.json()["response"]


# -----------------------------------------
# Get user input
# -----------------------------------------
user_input = input("You: ")


# -----------------------------------------
# Get descriptions of available tools
# -----------------------------------------
tool_descriptions = get_tool_descriptions()


# -----------------------------------------
# Initial prompt
# -----------------------------------------
prompt = f"""
You are an AI agent.

You have access to these tools:

{tool_descriptions}

Your job is to solve the user's request.

You may use one or more tools.

If you need a tool, return ONLY valid JSON.

Use this format:

{{
    "tool": "tool_name",
    "arguments": {{
        "argument_name": "value"
    }}
}}

If you have enough information to answer the user, return ONLY valid JSON:

{{
    "tool": "none",
    "answer": "your final answer"
}}

User request:
{user_input}
"""


# =========================================
# REAL AGENT LOOP
# =========================================

while True:

    # -------------------------------------
    # Ask LLM what to do
    # -------------------------------------
    response = ask_llm(prompt)

    print("\nLLM response:")
    print(response)


    # -------------------------------------
    # Convert JSON text into Python
    # -------------------------------------
    try:

        data = json.loads(response)

    except json.JSONDecodeError:

        print("\nInvalid JSON returned by LLM.")

        break


    # -------------------------------------
    # Get selected tool
    # -------------------------------------
    tool_name = data.get("tool")


    # -------------------------------------
    # Agent has finished
    # -------------------------------------
    if tool_name == "none":

        final_answer = data.get(
            "answer",
            "Done."
        )

        print("\nFinal answer:")
        print(final_answer)

        break


    # -------------------------------------
    # Check whether tool exists
    # -------------------------------------
    if tool_name not in TOOLS:

        print("\nUnknown tool:", tool_name)

        break


    # -------------------------------------
    # Get tool arguments
    # -------------------------------------
    arguments = data.get(
        "arguments",
        {}
    )


    # -------------------------------------
    # Execute selected tool
    # -------------------------------------
    result = execute_tool(
        tool_name,
        arguments
    )


    print("\nTool result:")
    print(result)


    # -------------------------------------
    # Give tool result back to LLM
    # -------------------------------------
    prompt = f"""
You are an AI agent.

Original user request:
{user_input}

You previously used this tool:
{tool_name}

The tool returned this result:
{result}

Now decide what to do next.

If you need another tool, return ONLY valid JSON:

{{
    "tool": "tool_name",
    "arguments": {{
        "argument_name": "value"
    }}
}}

If you have enough information to answer the user, return ONLY valid JSON:

{{
    "tool": "none",
    "answer": "your final answer"
}}
"""