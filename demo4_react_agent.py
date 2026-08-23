"""
Demo 4: ReAct Agent Pattern (Thought → Action → Observation)
Shows the fundamental agent loop that powers AI agents.
"""
import streamlit as st
import re
from llm_utils import call_llm

st.set_page_config(page_title="ReAct Agent Demo", page_icon="🔄", layout="wide")


# Simulated tools that the agent can use
AVAILABLE_TOOLS = {
    "check_disk": {
        "description": "Check disk usage on a server",
        "example": "check_disk(server='prod-srv-07', path='/var')",
        "simulate": lambda args: """Filesystem      Size  Used Avail Use% Mounted on
/dev/sda3       100G   94G   6G   94% /var

Top space consumers:
/var/log/nginx/       42G
/var/log/messages     18G
/var/tmp/             12G
/var/cache/           8G""",
    },
    "check_process": {
        "description": "List top processes by resource usage",
        "example": "check_process(server='prod-srv-07', sort_by='cpu')",
        "simulate": lambda args: """  PID USER     %CPU %MEM COMMAND
 4521 www-data  285  12  /usr/sbin/nginx: worker process
 4523 root      120  18  /usr/bin/java -Xmx8g -jar app-server.jar
 1102 root        8   2  /usr/bin/dockerd
 2241 nagios      2   1  /usr/local/nagios/bin/nrpe""",
    },
    "check_logs": {
        "description": "Search recent system logs",
        "example": "check_logs(server='prod-srv-07', pattern='error', lines=10)",
        "simulate": lambda args: """Jun 08 14:21:33 prod-srv-07 kernel: EXT4-fs error (device sda3): ext4_find_entry:1455: inode #2883: comm cleanup: reading directory lblock 0
Jun 08 14:21:34 prod-srv-07 nginx[4500]: [error] 4521#0: *284721 upstream timed out (110: Connection timed out) while connecting to upstream
Jun 08 14:22:01 prod-srv-07 systemd[1]: var-log-audit.mount: Failed with result 'timeout'
Jun 08 14:22:15 prod-srv-07 kernel: [Hardware Error]: Machine check events logged""",
    },
    "run_command": {
        "description": "Run a safe read-only command",
        "example": "run_command(server='prod-srv-07', cmd='uptime')",
        "simulate": lambda args: """ 14:23:01 up 342 days, 7:14,  3 users,  load average: 12.84, 11.22, 8.91""",
    },
}

REACT_SYSTEM = """You are a server management agent using the ReAct pattern.

Available tools:
- check_disk(server, path): Check disk usage
- check_process(server, sort_by): List top processes (sort_by: cpu|mem)
- check_logs(server, pattern, lines): Search system logs
- run_command(server, cmd): Run safe read-only commands

For each step, respond in EXACTLY this format:
THOUGHT: [your reasoning about what to do next]
ACTION: [tool_name(arguments)]

After receiving an observation, continue with another THOUGHT/ACTION or conclude with:
THOUGHT: [final reasoning]
ANSWER: [your final answer/recommendation]

Be methodical. Investigate before concluding."""


st.title("🔄 Demo 4: ReAct Agent Pattern")
st.markdown("**Thought → Action → Observation** — The fundamental loop that makes AI agents work")

# Visual explanation
with st.expander("📖 What is ReAct?", expanded=False):
    st.markdown("""
    **ReAct** (Reasoning + Acting) is the pattern behind all modern AI agents:

    ```
    Loop:
      1. THOUGHT  → LLM reasons about what it knows and what it needs
      2. ACTION   → LLM decides which tool to call
      3. OBSERVATION → Tool returns real data
      4. Repeat until the LLM has enough info to answer
    ```

    This is fundamentally different from just asking an LLM a question:
    - **Without ReAct:** LLM guesses based on training data (hallucination risk!)
    - **With ReAct:** LLM gathers real data, then reasons about it (grounded!)
    """)

col1, col2 = st.columns([2, 3])

with col1:
    st.subheader("🎯 Scenario")
    scenarios = {
        "Disk space alert": "Alert: prod-srv-07 /var at 94%. Investigate and recommend action.",
        "High CPU": "prod-srv-07 has load average >12. Find the cause.",
        "Custom": "",
    }
    selected = st.selectbox("Choose scenario:", list(scenarios.keys()))
    user_query = st.text_area("Agent task:", value=scenarios[selected], height=80)

    st.subheader("🛠️ Available Tools")
    for name, tool in AVAILABLE_TOOLS.items():
        st.markdown(f"- **{name}**: {tool['description']}")

with col2:
    st.subheader("🔄 Agent Execution Trace")

    if st.button("▶️ Run Agent", type="primary") and user_query:
        trace = []
        context = f"User request: {user_query}\n\n"

        # Simulate multi-step ReAct loop (3 iterations max for demo)
        for step in range(4):
            with st.spinner(f"Step {step + 1}: Thinking..."):
                response = call_llm(context + "What is your next step?", REACT_SYSTEM, temperature=0.3)

            # Parse THOUGHT and ACTION
            thought_match = re.search(r"THOUGHT:\s*(.+?)(?=\nACTION:|ANSWER:|$)", response, re.DOTALL)
            action_match = re.search(r"ACTION:\s*(.+?)(?=\n|$)", response)
            answer_match = re.search(r"ANSWER:\s*(.+)", response, re.DOTALL)

            thought = thought_match.group(1).strip() if thought_match else response[:200]

            # Display thought
            st.markdown(f"**Step {step + 1} — THOUGHT:**")
            st.info(thought)

            if answer_match:
                st.markdown("**FINAL ANSWER:**")
                st.success(answer_match.group(1).strip())
                break

            if action_match:
                action = action_match.group(1).strip()
                st.markdown(f"**ACTION:** `{action}`")

                # Simulate tool execution
                tool_name = action.split("(")[0].strip()
                if tool_name in AVAILABLE_TOOLS:
                    observation = AVAILABLE_TOOLS[tool_name]["simulate"](action)
                    st.markdown("**OBSERVATION:**")
                    st.code(observation, language="text")
                    context += f"\nStep {step+1}:\nTHOUGHT: {thought}\nACTION: {action}\nOBSERVATION: {observation}\n"
                else:
                    st.warning(f"Unknown tool: {tool_name}")
                    context += f"\nStep {step+1}:\nTHOUGHT: {thought}\nACTION: {action}\nOBSERVATION: Error - tool not found\n"
            else:
                # No action parsed, try to get final answer
                st.markdown("**Response:**")
                st.success(response[:500])
                break

            st.divider()

st.divider()
st.markdown("""
### 🏗️ How This Applies to Server Management

| Traditional Approach | ReAct Agent Approach |
|---------------------|---------------------|
| Human reads alert | Agent sees alert |
| Human SSHs into server | Agent calls check_disk(), check_logs() |
| Human correlates data mentally | Agent reasons in THOUGHT steps |
| Human writes incident report | Agent generates structured summary |
| ~15 minutes | ~30 seconds |

**But remember:** The agent proposes, humans approve. No auto-remediation without review!
""")
