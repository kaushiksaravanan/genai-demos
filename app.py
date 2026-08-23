"""
Main Launcher: GenAI & Agentic Systems Demo Suite
Run this to get a navigation page linking all demos.
"""
import streamlit as st
import subprocess
import sys
import os

st.set_page_config(page_title="GenAI Demos - Server Management", page_icon="🎯", layout="wide")

st.title("🎯 Generative AI & Agentic Systems")
st.markdown("### Demo Suite for Server Management Teams")
st.markdown("---")

demos = [
    {
        "num": 1,
        "title": "Tokenization & Context Windows",
        "icon": "🔤",
        "file": "demo1_tokenization.py",
        "desc": "How LLMs see text as tokens, context window sizes, cost estimation",
        "covers": "Slide 4-5: How LLMs Work, Tokens & Context",
        "interactive": True,
    },
    {
        "num": 2,
        "title": "LLM Interaction",
        "icon": "🤖",
        "file": "demo2_llm_interaction.py",
        "desc": "Live Gemini API calls — temperature effects, system prompts, persona comparison",
        "covers": "Slide 7-8: LLMs Deep Dive, Foundation Models",
        "interactive": True,
    },
    {
        "num": 3,
        "title": "Hallucinations & Safety",
        "icon": "⚠️",
        "file": "demo3_hallucinations.py",
        "desc": "Trigger hallucinations on purpose, then show grounding and safety patterns",
        "covers": "Slide 9: Hallucinations & Guardrails",
        "interactive": True,
    },
    {
        "num": 4,
        "title": "ReAct Agent Pattern",
        "icon": "🔄",
        "file": "demo4_react_agent.py",
        "desc": "Thought → Action → Observation loop with simulated server tools",
        "covers": "Slide 10-11: AI Agents, ReAct Pattern",
        "interactive": True,
    },
    {
        "num": 5,
        "title": "LangGraph Workflow Agent",
        "icon": "🔀",
        "file": "demo5_langgraph.py",
        "desc": "Full incident response workflow with state machine, human approval, execution",
        "covers": "Slide 12-14: Workflow Agents, LangGraph, Agent Architectures",
        "interactive": True,
    },
    {
        "num": 6,
        "title": "Model Context Protocol (MCP)",
        "icon": "🔌",
        "file": "demo6_mcp.py",
        "desc": "MCP concepts, live tool calling with Gemini, building your own MCP server",
        "covers": "Slide 15: Model Context Protocol",
        "interactive": True,
    },
]

# Display as cards
cols = st.columns(2)
for i, demo in enumerate(demos):
    with cols[i % 2]:
        with st.container(border=True):
            st.markdown(f"### {demo['icon']} Demo {demo['num']}: {demo['title']}")
            st.markdown(demo["desc"])
            st.caption(f"📑 {demo['covers']}")
            st.code(f"streamlit run {demo['file']}", language="bash")

st.divider()
st.markdown("## 🚀 Quick Start")
st.code("""
# Run any individual demo:
cd ~/genai-demos
streamlit run demo1_tokenization.py

# Or run a specific one:
streamlit run demo4_react_agent.py --server.port 8502
""", language="bash")

st.markdown("## 📋 Presentation Slide Mapping")
st.markdown("""
| Slide | Topic | Demo |
|-------|-------|------|
| 1-3 | Intro & Agenda | No demo needed |
| 4-5 | Tokens & Context Windows | **Demo 1** |
| 6 | AI Evolution Timeline | Slides only (visual) |
| 7-8 | LLMs & Foundation Models | **Demo 2** |
| 9 | Hallucinations | **Demo 3** |
| 10-11 | AI Agents & ReAct | **Demo 4** |
| 12-14 | LangGraph & Architectures | **Demo 5** |
| 15 | MCP | **Demo 6** |
| 16-17 | Server Mgmt Use Cases | Covered across all demos |
| 18-19 | Getting Started & Python | Code shown in demos |
| 20-21 | Takeaways & Resources | Slides only |
""")

st.markdown("## ⚡ What You Need to Add")
st.warning("""
**From your side (not automatable):**
1. **Your team's actual monitoring screenshots** — replace simulated data with real Nagios/Grafana/Prometheus views
2. **Real server log examples** — actual syslog/journalctl outputs from your landscape
3. **Team-specific use cases** — which scripts do you want to AI-enable first?
4. **Approval workflow** — who approves AI-suggested changes in your team?
5. **Security constraints** — which servers can the AI access? VPN/bastion requirements?
""")
