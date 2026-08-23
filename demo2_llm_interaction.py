"""
Demo 2: LLM Interaction — Temperature, System Prompts, and Response Behavior
Live interaction showing how parameters affect output.
"""
import streamlit as st
import time
from llm_utils import call_llm

st.set_page_config(page_title="LLM Interaction Demo", page_icon="🤖", layout="wide")


st.title("🤖 Demo 2: LLM Interaction")
st.markdown("**See how system prompts and temperature change LLM behavior**")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Configuration")

    system_prompts = {
        "None (default)": "",
        "Server Admin Expert": "You are a senior Linux server administrator with 15 years of experience. Give concise, actionable answers with specific commands. Always mention potential risks.",
        "DevOps/SRE Engineer": "You are a Site Reliability Engineer. Interpret all questions through the lens of uptime, observability, and incident response. Reference monitoring tools (Prometheus, Grafana, Nagios) and automation (Ansible, Terraform) where relevant.",
        "Cautious Assistant": "You are extremely cautious. For every suggestion, list at least 3 things that could go wrong. Never recommend running commands in production without explicit backup steps.",
        "One-liner Bot": "Answer in exactly one sentence. No exceptions. No bullet points. Just one clear sentence.",
    }

    selected_system = st.selectbox("System Prompt:", list(system_prompts.keys()))
    system_prompt = system_prompts[selected_system]

    if system_prompt:
        with st.expander("System prompt content"):
            st.code(system_prompt)

    temperature = st.slider("Temperature", 0.0, 2.0, 0.7, 0.1,
                            help="0 = deterministic, 1 = creative, 2 = chaotic")

    st.markdown("""
    | Temperature | Behavior |
    |-------------|----------|
    | 0.0 | Always same answer (deterministic) |
    | 0.3-0.7 | Balanced (good default) |
    | 1.0+ | Creative/varied |
    | 2.0 | Near-random |
    """)

with col2:
    st.subheader("Ask a question")

    sample_questions = {
        "Custom": "",
        "Server disk full": "The /var partition on prod-srv-07 is at 98%. What should I do?",
        "High CPU": "A Java process is consuming 400% CPU on our application server. How do I diagnose?",
        "Explain concept": "What is a kernel panic and when does it happen?",
        "Write a script": "Write a bash one-liner to find the 10 largest files modified in the last 24 hours.",
    }

    selected_q = st.selectbox("Sample questions:", list(sample_questions.keys()))
    user_input = st.text_area("Your prompt:",
                              value=sample_questions[selected_q],
                              height=100,
                              placeholder="Ask anything about server management...")

    if st.button("🚀 Send to LLM", type="primary") and user_input:
        with st.spinner("Calling LLM (Gemini → Groq fallback)..."):
            start = time.time()
            response = call_llm(user_input, system_prompt, temperature)
            elapsed = time.time() - start

        st.success(f"Response received in {elapsed:.1f}s")
        st.markdown(response)

        # Temperature comparison
        if st.checkbox("Compare: Run same prompt 3x to show temperature effect"):
            st.subheader("Same prompt, 3 calls (shows randomness)")
            cols = st.columns(3)
            for i, c in enumerate(cols):
                with c:
                    with st.spinner(f"Call {i+1}..."):
                        r = call_llm(user_input, system_prompt, temperature)
                    st.markdown(f"**Run {i+1}:**")
                    st.markdown(r[:500])

st.divider()

# Interactive comparison section
st.subheader("🔬 Side-by-Side: Same Question, Different System Prompts")
compare_prompt = st.text_input("Prompt for comparison:",
                               value="The server is running slow. What should I check?")

if st.button("Compare All Personas") and compare_prompt:
    cols = st.columns(3)
    personas = ["Server Admin Expert", "DevOps/SRE Engineer", "One-liner Bot"]
    for i, persona in enumerate(personas):
        with cols[i]:
            st.markdown(f"**{persona}**")
            with st.spinner("..."):
                r = call_llm(compare_prompt, system_prompts[persona], 0.5)
            st.markdown(r[:600])

st.divider()
st.markdown("""
**Key Takeaways:**
- **System prompts** shape behavior without retraining the model
- **Temperature** controls randomness — use 0 for scripts/commands, 0.7 for explanations
- The same model can act as different "experts" based on framing
""")
