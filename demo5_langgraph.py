"""
Demo 5: LangGraph Workflow Agent
Shows stateful multi-step agent orchestration with visual state machine.
"""
import streamlit as st
import time
from llm_utils import call_llm

st.set_page_config(page_title="LangGraph Demo", page_icon="🔀", layout="wide")


st.title("🔀 Demo 5: LangGraph Workflow Agent")
st.markdown("**Stateful orchestration** — Beyond simple ReAct, into production-grade agent workflows")

tab1, tab2, tab3 = st.tabs(["📊 Concept", "🎮 Interactive Workflow", "💻 Code"])

with tab1:
    st.subheader("Why LangGraph over raw ReAct?")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        ### ❌ Raw ReAct Problems
        - No state management between steps
        - No branching logic
        - No human-in-the-loop checkpoints
        - No retry/error handling
        - Can loop forever
        - No audit trail
        """)
    with col2:
        st.markdown("""
        ### ✅ LangGraph Adds
        - **Typed state** persisted between nodes
        - **Conditional edges** (if/else routing)
        - **Human approval nodes** (breakpoints)
        - **Built-in error handling** per node
        - **Max iterations** with graceful exit
        - **Full execution trace** for audit
        """)

    st.divider()
    st.subheader("Server Incident Response — As a State Machine")

    # ASCII state machine diagram
    st.code("""
    ┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
    │   TRIAGE    │────▶│  INVESTIGATE │────▶│   PLAN_FIX      │
    │ (classify   │     │ (gather data │     │ (generate        │
    │  severity)  │     │  from tools) │     │  remediation)    │
    └─────────────┘     └──────────────┘     └─────────────────┘
          │                    │                       │
          │ P1?               │ Need more?           │
          ▼                    ▼                       ▼
    ┌─────────────┐     ┌──────────────┐     ┌─────────────────┐
    │  ESCALATE   │     │   (loop)     │     │ HUMAN_APPROVE   │
    │ (page oncall│     └──────────────┘     │ (wait for OK)   │
    │  + manager) │                           └─────────────────┘
    └─────────────┘                                   │
                                                      │ Approved?
                                                      ▼
                                              ┌─────────────────┐
                                              │    EXECUTE      │
                                              │ (run fix with   │
                                              │  rollback plan) │
                                              └─────────────────┘
                                                      │
                                                      ▼
                                              ┌─────────────────┐
                                              │    VERIFY       │
                                              │ (confirm fix    │
                                              │  worked)        │
                                              └─────────────────┘
    """, language="text")

with tab2:
    st.subheader("🎮 Simulate Incident Response Workflow")

    # State definition
    if "workflow_state" not in st.session_state:
        st.session_state.workflow_state = {
            "current_node": "START",
            "severity": None,
            "findings": [],
            "plan": None,
            "approved": False,
            "executed": False,
            "history": [],
        }

    state = st.session_state.workflow_state

    # Incident input
    incident = st.text_area(
        "Incident description:",
        value="ALERT: prod-db-01 memory usage at 97%, PostgreSQL response times degraded, application users reporting timeouts",
        height=80,
    )

    # Progress indicator
    nodes = ["START", "TRIAGE", "INVESTIGATE", "PLAN_FIX", "HUMAN_APPROVE", "EXECUTE", "VERIFY", "DONE"]
    current_idx = nodes.index(state["current_node"]) if state["current_node"] in nodes else 0
    progress = current_idx / (len(nodes) - 1)
    st.progress(progress, text=f"Current: **{state['current_node']}** ({current_idx}/{len(nodes)-1})")

    # Node execution
    if state["current_node"] == "START":
        if st.button("▶️ Start Workflow", type="primary"):
            state["current_node"] = "TRIAGE"
            state["history"].append(("START", "Workflow initiated"))
            st.rerun()

    elif state["current_node"] == "TRIAGE":
        st.markdown("### 🏷️ TRIAGE Node")
        st.markdown("*Classifying incident severity...*")

        with st.spinner("AI triaging..."):
            triage_result = call_llm(
                f"Classify this server incident severity (P1-Critical, P2-High, P3-Medium, P4-Low) and explain in 2 sentences:\n\n{incident}",
                "You are an incident triage system. Respond with SEVERITY: P1/P2/P3/P4 on the first line, then a brief explanation.",
                temperature=0.3,
            )

        st.info(triage_result)
        severity = "P1" if "P1" in triage_result[:20] else "P2" if "P2" in triage_result[:20] else "P3"
        state["severity"] = severity
        state["history"].append(("TRIAGE", f"Severity: {severity}"))

        if severity == "P1":
            st.error("🚨 P1 detected — would escalate to oncall in production")

        if st.button("Continue → INVESTIGATE"):
            state["current_node"] = "INVESTIGATE"
            st.rerun()

    elif state["current_node"] == "INVESTIGATE":
        st.markdown("### 🔍 INVESTIGATE Node")
        st.markdown("*Gathering data from monitoring tools...*")

        # Simulated tool outputs
        findings = {
            "Memory check": "PostgreSQL shared_buffers: 32GB / 64GB total RAM (97% used)\nOOM killer invoked 3 times in last hour\nTop consumer: pg_dump backup process (user: backup_svc)",
            "Process list": "PID 18294 postgres: writer process 48GB RSS\nPID 18301 postgres: autovacuum worker 8GB RSS\nPID 19442 pg_dump --format=custom production_db 12GB RSS\n47 blocked connections waiting on lock",
            "Recent logs": "2026-06-08 14:15:22 [CRITICAL] out_of_memory: killed process 18301 (autovacuum)\n2026-06-08 14:14:58 [WARNING] could not fork new process for connection: Cannot allocate memory\n2026-06-08 14:10:01 [INFO] pg_dump started by cron job /etc/cron.d/db-backup",
        }

        for check, result in findings.items():
            with st.expander(f"📋 {check}", expanded=True):
                st.code(result)

        state["findings"] = list(findings.values())
        state["history"].append(("INVESTIGATE", f"Gathered {len(findings)} data points"))

        if st.button("Continue → PLAN FIX"):
            state["current_node"] = "PLAN_FIX"
            st.rerun()

    elif state["current_node"] == "PLAN_FIX":
        st.markdown("### 📝 PLAN_FIX Node")
        st.markdown("*Generating remediation plan...*")

        with st.spinner("AI generating plan..."):
            plan = call_llm(
                f"""Based on these investigation findings, generate a remediation plan:
{chr(10).join(state['findings'])}

Format as numbered steps. Include rollback plan. Mark each step as SAFE or NEEDS_APPROVAL.""",
                "You are a senior database and Linux systems administrator. Generate safe, specific remediation steps.",
                temperature=0.3,
            )

        st.markdown(plan)
        state["plan"] = plan
        state["history"].append(("PLAN_FIX", "Plan generated"))

        if st.button("Continue → HUMAN APPROVE"):
            state["current_node"] = "HUMAN_APPROVE"
            st.rerun()

    elif state["current_node"] == "HUMAN_APPROVE":
        st.markdown("### 👤 HUMAN_APPROVE Node (Breakpoint)")
        st.warning("⏸️ **Workflow paused — waiting for human approval**")
        st.markdown("*In production, this sends a Slack/Teams notification and waits.*")

        st.markdown("**Proposed plan:**")
        st.markdown(state.get("plan", "No plan generated"))

        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Approve", type="primary"):
                state["approved"] = True
                state["current_node"] = "EXECUTE"
                state["history"].append(("HUMAN_APPROVE", "Approved"))
                st.rerun()
        with col2:
            if st.button("❌ Reject"):
                state["current_node"] = "PLAN_FIX"
                state["history"].append(("HUMAN_APPROVE", "Rejected — back to planning"))
                st.rerun()

    elif state["current_node"] == "EXECUTE":
        st.markdown("### ⚡ EXECUTE Node")
        st.markdown("*Executing approved remediation...*")

        steps = ["Killing pg_dump backup process...", "Releasing blocked connections...", "Clearing OS page cache...", "Verifying memory freed..."]
        progress_bar = st.progress(0)
        for i, step in enumerate(steps):
            st.write(f"  ▸ {step}")
            time.sleep(0.5)
            progress_bar.progress((i + 1) / len(steps))

        st.success("Execution complete!")
        state["executed"] = True
        state["history"].append(("EXECUTE", "Remediation executed"))

        if st.button("Continue → VERIFY"):
            state["current_node"] = "VERIFY"
            st.rerun()

    elif state["current_node"] == "VERIFY":
        st.markdown("### ✔️ VERIFY Node")
        st.markdown("*Confirming fix was effective...*")

        st.code("""Memory check (post-fix):
Server memory usage: 41GB / 64GB (64%) ✓
Blocked connections: 0 ✓
PostgreSQL response time: 8ms (normal) ✓
Active backup jobs: 0 (killed) ✓""")

        st.success("✅ All checks passed — incident resolved!")
        state["current_node"] = "DONE"
        state["history"].append(("VERIFY", "Fix verified successful"))
        st.balloons()

    elif state["current_node"] == "DONE":
        st.success("🎉 Workflow Complete!")

    # Reset button
    if state["current_node"] != "START":
        if st.button("🔄 Reset Workflow"):
            st.session_state.workflow_state = {
                "current_node": "START", "severity": None, "findings": [],
                "plan": None, "approved": False, "executed": False, "history": [],
            }
            st.rerun()

    # Audit trail
    with st.expander("📜 Execution History (Audit Trail)"):
        for node, detail in state["history"]:
            st.markdown(f"- **{node}**: {detail}")

with tab3:
    st.subheader("💻 LangGraph Code Structure")
    st.markdown("Here's what the actual Python code looks like:")

    st.code("""
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Literal

# 1. Define state schema
class IncidentState(TypedDict):
    incident: str
    severity: str
    findings: list[str]
    plan: str
    approved: bool
    result: str

# 2. Define node functions
def triage(state: IncidentState) -> dict:
    severity = llm.classify(state["incident"])
    return {"severity": severity}

def investigate(state: IncidentState) -> dict:
    findings = [
        tools.check_memory(state["incident"]),
        tools.check_processes(state["incident"]),
        tools.check_logs(state["incident"]),
    ]
    return {"findings": findings}

def plan_fix(state: IncidentState) -> dict:
    plan = llm.generate_plan(state["findings"])
    return {"plan": plan}

def execute(state: IncidentState) -> dict:
    result = tools.run_remediation(state["plan"])
    return {"result": result}

# 3. Define routing logic
def route_after_triage(state) -> Literal["escalate", "investigate"]:
    return "escalate" if state["severity"] == "P1" else "investigate"

def route_after_approval(state) -> Literal["execute", "plan_fix"]:
    return "execute" if state["approved"] else "plan_fix"

# 4. Build the graph
graph = StateGraph(IncidentState)
graph.add_node("triage", triage)
graph.add_node("investigate", investigate)
graph.add_node("plan_fix", plan_fix)
graph.add_node("human_approve", lambda s: s)  # Breakpoint node
graph.add_node("execute", execute)

graph.add_edge(START, "triage")
graph.add_conditional_edges("triage", route_after_triage)
graph.add_edge("investigate", "plan_fix")
graph.add_edge("plan_fix", "human_approve")
graph.add_conditional_edges("human_approve", route_after_approval)
graph.add_edge("execute", END)

# 5. Compile and run
app = graph.compile(interrupt_before=["human_approve"])
result = app.invoke({"incident": "Memory alert on prod-db-01"})
    """, language="python")

    st.info("""
    **Key LangGraph concepts shown:**
    - `StateGraph` — typed state flows through all nodes
    - `add_conditional_edges` — if/else routing based on state
    - `interrupt_before` — human-in-the-loop breakpoints
    - Each node returns a dict that updates state
    - Full execution is replayable and auditable
    """)
