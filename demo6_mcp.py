"""
Demo 6: Model Context Protocol (MCP)
Shows how MCP exposes tools to LLM agents in a standardized way.
"""
import streamlit as st
import json
from llm_utils import call_llm_with_tools, call_llm

st.set_page_config(page_title="MCP Demo", page_icon="🔌", layout="wide")


st.title("🔌 Demo 6: Model Context Protocol (MCP)")
st.markdown("**The USB-C of AI** — A standard protocol for connecting LLMs to tools")

tab1, tab2, tab3 = st.tabs(["📖 Concept", "🔧 Live Tool Calling", "🏗️ Build Your Own"])

with tab1:
    st.subheader("The Problem MCP Solves")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        ### Before MCP: N×M Problem
        Every AI app needs custom integrations for every tool.

        ```
        Claude  ──custom──▶ Nagios
        Claude  ──custom──▶ Grafana
        Claude  ──custom──▶ JIRA
        GPT     ──custom──▶ Nagios (different!)
        GPT     ──custom──▶ Grafana (different!)
        Gemini  ──custom──▶ Nagios (yet another!)
        ```
        **6 different integrations** for 3 LLMs × 2 tools
        """)
    with col2:
        st.markdown("""
        ### After MCP: N+M Solution
        One standard protocol. Any LLM talks to any tool.

        ```
        Claude  ─┐
        GPT     ─┼── MCP ──┬──▶ Nagios MCP Server
        Gemini  ─┘          ├──▶ Grafana MCP Server
                            └──▶ JIRA MCP Server
        ```
        **5 total implementations** (3 clients + 2 servers)
        """)

    st.divider()
    st.subheader("MCP Architecture")
    st.code("""
    ┌─────────────────┐         ┌──────────────────┐         ┌────────────────┐
    │   LLM Client    │  JSON   │   MCP Server     │         │  Actual Tool   │
    │ (Claude, GPT,   │◀──────▶│ (lightweight     │────────▶│ (Nagios API,   │
    │  your agent)    │  RPC    │  adapter)        │         │  SSH, kubectl) │
    └─────────────────┘         └──────────────────┘         └────────────────┘
                                        │
                                Exposes:
                                - tools (functions the LLM can call)
                                - resources (data the LLM can read)
                                - prompts (templates for common tasks)
    """, language="text")

    st.subheader("Real-World Server Management MCP Servers")
    mcp_examples = [
        ("🖥️ Server Health MCP", "Exposes: check_cpu, check_memory, check_disk, list_processes, tail_logs", "Your monitoring stack via standard interface"),
        ("📊 Prometheus/Grafana MCP", "Exposes: query_metrics, get_alerts, list_dashboards, get_panel_data", "Metrics and alerting accessible to AI"),
        ("🎫 ServiceNow MCP", "Exposes: create_incident, update_ticket, search_kb, list_changes", "ITSM integration for automated incident management"),
        ("☸️ Kubernetes MCP", "Exposes: get_pods, describe_node, check_events, scale_deployment", "K8s cluster management"),
    ]

    for name, tools, desc in mcp_examples:
        with st.expander(name):
            st.markdown(f"**Tools:** {tools}")
            st.markdown(f"**Use case:** {desc}")

with tab2:
    st.subheader("🔧 Live: LLM Tool Calling (Gemini Function Calling)")
    st.markdown("This demonstrates the core mechanism MCP is built on — structured tool invocations.")

    # Define tools schema (Gemini function calling format)
    tools_schema = [
        {
            "name": "check_server_health",
            "description": "Check the health status of a server including CPU, memory, and disk",
            "parameters": {
                "type": "object",
                "properties": {
                    "hostname": {"type": "string", "description": "Server hostname"},
                    "checks": {
                        "type": "array",
                        "items": {"type": "string", "enum": ["cpu", "memory", "disk", "network"]},
                        "description": "Which health checks to run",
                    },
                },
                "required": ["hostname"],
            },
        },
        {
            "name": "search_logs",
            "description": "Search server logs for patterns",
            "parameters": {
                "type": "object",
                "properties": {
                    "hostname": {"type": "string"},
                    "pattern": {"type": "string", "description": "Regex pattern to search for"},
                    "severity": {"type": "string", "enum": ["INFO", "WARNING", "ERROR", "CRITICAL"]},
                    "last_minutes": {"type": "integer", "description": "Search window in minutes"},
                },
                "required": ["hostname", "pattern"],
            },
        },
        {
            "name": "create_incident",
            "description": "Create a new incident ticket",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "severity": {"type": "string", "enum": ["P1", "P2", "P3", "P4"]},
                    "description": {"type": "string"},
                    "assigned_team": {"type": "string"},
                },
                "required": ["title", "severity", "description"],
            },
        },
    ]

    st.markdown("**Available tools (exposed via MCP schema):**")
    for tool in tools_schema:
        st.json(tool, expanded=False)

    user_request = st.text_input(
        "Natural language request:",
        value="Check if prod-web-01 has any critical memory or CPU issues, and look for OOM errors in the last 30 minutes",
    )

    if st.button("🚀 Send to LLM with tools", type="primary") and user_request:
        with st.spinner("LLM deciding which tools to call..."):
            result = call_llm_with_tools(user_request, tools_schema)

        if "error" in result:
            st.error(f"API error: {result}")
        elif "fallback" in result:
            st.info("(Used Groq fallback — showing tool selection reasoning)")
            st.markdown(result["text"])
        else:
            candidates = result.get("candidates", [])
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [])
                for part in parts:
                    if "functionCall" in part:
                        fc = part["functionCall"]
                        st.success(f"🔧 LLM wants to call: **{fc['name']}**")
                        st.json(fc.get("args", {}))

                        # Simulate tool response
                        st.markdown("**Simulated tool response:**")
                        if "health" in fc["name"]:
                            st.code(json.dumps({
                                "hostname": fc["args"].get("hostname", "unknown"),
                                "status": "WARNING",
                                "cpu_percent": 78,
                                "memory_percent": 94,
                                "memory_details": {"total_gb": 512, "used_gb": 481, "swap_used_gb": 2.1},
                            }, indent=2))
                        elif "logs" in fc["name"]:
                            st.code(json.dumps({
                                "matches": 3,
                                "entries": [
                                    {"timestamp": "2026-06-08T14:15:22Z", "level": "CRITICAL", "message": "OOM killer invoked for process hdbindexserver"},
                                    {"timestamp": "2026-06-08T14:14:58Z", "level": "ERROR", "message": "memory allocation failed: 2048MB requested"},
                                ]
                            }, indent=2))
                    elif "text" in part:
                        st.markdown(part["text"])

with tab3:
    st.subheader("🏗️ Build Your Own MCP Server (Python)")
    st.markdown("It's surprisingly simple to expose your tools via MCP:")

    st.code("""
# server_health_mcp.py
from mcp.server import Server
from mcp.types import Tool, TextContent
import subprocess

server = Server("server-health")

@server.tool()
async def check_disk(hostname: str, path: str = "/") -> str:
    \"\"\"Check disk usage on a remote server.\"\"\"
    result = subprocess.run(
        ["ssh", hostname, f"df -h {path}"],
        capture_output=True, text=True, timeout=10
    )
    return result.stdout

@server.tool()
async def check_memory(hostname: str) -> str:
    \"\"\"Check memory usage on a remote server.\"\"\"
    result = subprocess.run(
        ["ssh", hostname, "free -h"],
        capture_output=True, text=True, timeout=10
    )
    return result.stdout

@server.tool()
async def tail_logs(hostname: str, log_path: str = "/var/log/messages",
                    lines: int = 50, grep: str = "") -> str:
    \"\"\"Tail recent log entries, optionally filtering by pattern.\"\"\"
    cmd = f"tail -n {lines} {log_path}"
    if grep:
        cmd += f" | grep -i '{grep}'"
    result = subprocess.run(
        ["ssh", hostname, cmd],
        capture_output=True, text=True, timeout=10
    )
    return result.stdout

# Run: python -m mcp.server.stdio server_health_mcp.py
    """, language="python")

    st.markdown("""
    ### Configure in Claude Desktop / Claude Code:

    ```json
    {
      "mcpServers": {
        "server-health": {
          "command": "python",
          "args": ["server_health_mcp.py"],
          "env": {"SSH_KEY": "/path/to/key"}
        }
      }
    }
    ```

    That's it! Now any MCP-compatible LLM client can:
    - Discover your tools automatically
    - Call them with proper typed arguments
    - Get structured responses back
    """)

    st.info("""
    **For your team's Python automation:**
    Any existing Python function can become an MCP tool in ~5 lines of wrapper code.
    Your existing monitoring scripts, health checks, and automation — all exposable to AI agents.
    """)

st.divider()
st.markdown("""
**Key Takeaway:** MCP is the standard that lets you write tools ONCE and use them with ANY AI agent.
Your team's Python automation scripts are already 90% of an MCP server — just add the protocol wrapper.
""")
