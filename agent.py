import tempfile
import subprocess
import os, json
# from openai import OpenAI

from safe_model import SafeModel

model = SafeModel()




AGENT_SYSTEM_PROMPT = """
You are an agent that can perform multi-step actions.
You have TWO possible actions:

1. "run_code" – you will return Python code to execute.
   The code MUST print the final result of that step to stdout.

2. "finish" – you will return a final JSON object for the USER.

You MUST respond ONLY with JSON in the form:

For running code:

{
  "action": "run_code",
  "code": "print('hello')"
}

For finishing the task:

{
  "action": "finish",
  "final": {
    "type": "<short string describing the kind of data, e.g. 'system_users'>",
    "result": <the data you computed, e.g. a list of users>,
    "metadata": {}
  }
}

Notes:
- "final" MUST be a JSON object with keys: "type", "result", "metadata".
- "metadata" MUST be a JSON object (may be empty).
- NEVER include explanations or anything outside this top-level JSON.

When returning JSON:
- Use ONLY double quotes (") for all keys and string values.
- NEVER use single quotes (').
- NEVER output Python dictionaries.
- NEVER output trailing commas.
- NEVER output comments.
- The entire response MUST be valid JSON that json.loads() can parse.
- Use DOUBLE QUOTES only.
- No single quotes anywhere.
- No Python dict syntax.
- No trailing commas.
- No comments.
- The entire response MUST be valid JSON that parses with json.loads().


Before assuming any directory structure, always run code to print the contents
of the relevant directories. Use actual inspection instead of guessing.

"""

def strip_zw(text: str):
    ZW = "".join([
        "\u200b", "\u200c", "\u200d", "\ufeff"
    ])
    return "".join(ch for ch in text if ch not in ZW)



def llm_agent_call(history):
    messages = [{"role": "system", "content": AGENT_SYSTEM_PROMPT}] + history
    return model.chat(messages)




def execute_python(code: str) -> str:
    """Write code to a temp file and execute it."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
        f.write(code)
        path = f.name

    result = subprocess.run(
        ["python3", path],
        text=True,
        capture_output=True
    )

    stdout = (result.stdout or "").strip()
    stderr = (result.stderr or "").strip()

    # Combine for agent context:
    if stderr:
        return f"[error]\n{stderr}"
    return stdout




def agent_step(user_prompt: str):
    """A minimal multi-step agent loop."""
    history = [{"role": "user", "content": user_prompt}]

    while True:
        # 1. Ask the LLM what action to take
        llm_raw = llm_agent_call(history)
        # print("\n=== LLM RAW JSON ===")
        # print(llm_raw)

        raw = llm_raw

        # Remove zero-width stego chars before JSON parsing
        clean_raw = strip_zw(raw)

        try:
            payload = json.loads(clean_raw)
        except:
            return f"❌ LLM returned non-JSON:\n{clean_raw}"


        action = payload.get("action")

        # ——————————————————————————
        # ACTION: run_code
        # ——————————————————————————
        if action == "run_code":
            code = payload.get("code")
            if not isinstance(code, str):
                return f"❌ Invalid run_code payload:\n{raw}"

            # Execute the Python code
            # print("\n=== LLM GENERATED CODE ===")
            # print(code)

            stdout = execute_python(code)
            # print("\n=== PYTHON EXECUTION OUTPUT ===")
            # print(stdout)

            history.append({"role": "assistant", "content": raw})
            history.append({
                "role": "user",
                "content": f"Execution output:\n{stdout}"
            })


            continue

        # ——————————————————————————
        # ACTION: finish
        # ——————————————————————————
        elif action == "finish":
            final = payload.get("final")

            if not isinstance(final, dict):
                return f"❌ finish missing final object:\n{raw}"

            if not {"type", "result", "metadata"} <= set(final.keys()):
                return f"❌ final object missing required keys:\n{raw}"

            print("\n===  SAFETY STATE ===")
            print(json.dumps(model.safety_state, indent=2))

            print("\n=== FINAL OUTPUT ===")
            print(json.dumps(final, indent=2))
            return final

        else:
            return f"❌ Invalid action:\n{raw}"



