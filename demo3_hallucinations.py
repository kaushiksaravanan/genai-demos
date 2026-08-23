"""
Demo 3: Hallucinations & Safety
Demonstrates LLM hallucinations and techniques to mitigate them.
"""
import streamlit as st
from llm_utils import call_llm

st.set_page_config(page_title="Hallucination Demo", page_icon="⚠️", layout="wide")


st.title("⚠️ Demo 3: Hallucinations & Safety Mechanisms")
st.markdown("**LLMs can confidently generate false information.** This demo shows the problem and solutions.")

tab1, tab2, tab3 = st.tabs(["🎭 Trigger Hallucinations", "🛡️ Grounding Techniques", "🔒 Safety Patterns"])

with tab1:
    st.subheader("Hallucination Examples")
    st.warning("LLMs predict the *most likely next token* — they don't 'know' facts. This means they can fabricate plausible-sounding information.")

    hallucination_prompts = {
        "Nonexistent Linux command": "Explain how the 'srvdiag --deep-inspect' command works on RHEL 9.",
        "Fake Kubernetes resource": "What does the 'kubectl get hypervisors --all-namespaces' command show and when should I use it?",
        "Made-up kernel parameter": "What is the optimal value for net.ipv4.tcp_turbo_mode in /etc/sysctl.conf?",
        "Fake monitoring tool": "How do I configure Prometheus AlertManager's 'predictive_scaling' module for auto-remediation?",
        "Fictional RFC": "What does RFC 9847 specify about server health check protocols?",
    }

    selected = st.selectbox("Choose a trap question:", list(hallucination_prompts.keys()))
    prompt = hallucination_prompts[selected]

    st.code(prompt, language="text")
    st.caption("⬆️ These reference things that DON'T EXIST. Watch the LLM confidently explain them anyway.")

    if st.button("🎭 Ask the LLM (no grounding)", type="primary"):
        with st.spinner("Generating potentially hallucinated response..."):
            response = call_llm(prompt, temperature=0.7)
        st.error("⚠️ The following may contain hallucinated information:")
        st.markdown(response)
        st.markdown("---")
        st.info("**Reality check:** The thing asked about doesn't exist. The LLM fabricated a plausible answer because it predicts likely token sequences, not verified facts.")

with tab2:
    st.subheader("Grounding: How to Reduce Hallucinations")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### ❌ Ungrounded Prompt")
        ungrounded = "What are the best kernel parameters for a high-traffic nginx server?"
        st.code(ungrounded)

    with col2:
        st.markdown("### ✅ Grounded Prompt (with context)")
        grounded_system = """You are a server configuration assistant.
ONLY answer based on the provided documentation.
If the information is not in the documentation, say "I don't have this information in the provided docs."
Never make up configuration values."""

        grounded_prompt = """Based on this documentation excerpt:

---
RHEL 9 Performance Tuning Guide - High-Traffic Web Servers:
- net.core.somaxconn = 65535
- net.ipv4.tcp_max_syn_backlog = 65535
- net.ipv4.tcp_tw_reuse = 1
- vm.swappiness = 10
- fs.file-max = 2097152
---

Question: What kernel parameters should I set for a high-traffic web server?"""
        st.code(grounded_prompt, language="text")

    if st.button("Compare Both Approaches"):
        col1, col2 = st.columns(2)
        with col1:
            with st.spinner("Ungrounded..."):
                r1 = call_llm(ungrounded, temperature=0.7)
            st.error("Ungrounded Response (may hallucinate values):")
            st.markdown(r1[:800])
        with col2:
            with st.spinner("Grounded..."):
                r2 = call_llm(grounded_prompt, grounded_system, temperature=0.2)
            st.success("Grounded Response (constrained to docs):")
            st.markdown(r2[:800])

    st.divider()
    st.markdown("""
    ### Grounding Techniques Ranked

    | Technique | Effectiveness | Server Mgmt Example |
    |-----------|--------------|---------------------|
    | RAG (Retrieval-Augmented Generation) | ⭐⭐⭐⭐⭐ | Feed actual runbooks into context |
    | System prompt constraints | ⭐⭐⭐⭐ | "Only use info from provided logs" |
    | Low temperature (0.0-0.3) | ⭐⭐⭐ | For command generation |
    | Structured output (JSON) | ⭐⭐⭐ | Force specific fields only |
    | Verification prompts | ⭐⭐ | "Are you sure? Cite your source." |
    """)

with tab3:
    st.subheader("Safety Patterns for Production Use")

    st.markdown("""
    ### The Human-in-the-Loop Pattern

    For server management, **NEVER** let an LLM execute commands directly in production without review.
    """)

    st.code("""
# SAFE: Generate → Review → Execute
def safe_remediation(issue_description):
    # Step 1: LLM generates a plan
    plan = llm.generate(f"Suggest fix for: {issue_description}")

    # Step 2: Human reviews
    approved = human_review(plan)  # Slack notification, approval UI

    # Step 3: Only execute if approved
    if approved:
        execute_with_rollback(plan)
    """, language="python")

    st.markdown("""
    ### Confidence Scoring Pattern
    """)

    confidence_prompt = st.text_input(
        "Test confidence scoring:",
        value="Should I restart the nginx service on our production load balancer during business hours?"
    )

    if st.button("Get answer with confidence score"):
        system = """Answer the question and rate your confidence on a scale of 1-10.
Format your response as:
ANSWER: [your answer]
CONFIDENCE: [1-10]
REASONING: [why this confidence level]
ACTION_RISK: [LOW/MEDIUM/HIGH/CRITICAL]

If confidence is below 7, explicitly state what additional information you need."""

        with st.spinner("..."):
            r = call_llm(confidence_prompt, system, temperature=0.3)
        st.markdown(r)

    st.divider()
    st.error("""
    🚨 **Golden Rules for Server Mgmt AI:**
    1. Never auto-execute destructive commands (rm, kill, stop, DROP)
    2. Always require human approval for production changes
    3. Log all AI-suggested actions for audit trail
    4. Use confidence thresholds — reject low-confidence suggestions
    5. Validate against known-good patterns (runbooks, SOPs)
    """)
