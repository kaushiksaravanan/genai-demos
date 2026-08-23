"""
Demo 1: Tokenization & Context Windows
Shows how text becomes tokens, counts them, and visualizes context window limits.
"""
import streamlit as st
import tiktoken
import requests

st.set_page_config(page_title="Tokenization Demo", page_icon="🔤", layout="wide")

st.title("🔤 Demo 1: Tokenization & Context Windows")
st.markdown("**How LLMs see your text** — not as words, but as tokens (subword pieces)")

# Sidebar config
st.sidebar.header("Configuration")
model_encoding = st.sidebar.selectbox(
    "Encoding (model family)",
    ["cl100k_base (GPT-4/Claude)", "o200k_base (GPT-4o)"],
)
enc_name = model_encoding.split(" ")[0]
enc = tiktoken.get_encoding(enc_name)

# Context window comparison data
CONTEXT_WINDOWS = {
    "GPT-3.5 (2023)": 4_096,
    "GPT-4 (2023)": 8_192,
    "GPT-4-Turbo (2024)": 128_000,
    "Claude 3.5 Sonnet": 200_000,
    "Claude Opus 4": 200_000,
    "Gemini 2.5 Pro": 1_000_000,
}

col1, col2 = st.columns([3, 2])

with col1:
    st.subheader("Enter text to tokenize")
    sample_texts = {
        "Simple English": "The server CPU usage exceeded 95% threshold.",
        "Python code": "def check_health(host):\n    response = requests.get(f'http://{host}/health')\n    return response.status_code == 200",
        "Server log entry": "Jun 08 14:22:33 prod-web-03 kernel: [Hardware Error]: CPU6: Machine Check: 0 Bank 5: ee2000000040110a. OOM killer invoked for process nginx (pid 4521)",
        "Ansible playbook": "- name: Restart nginx\n  hosts: web_servers\n  tasks:\n    - systemd:\n        name: nginx\n        state: restarted\n      notify: check_health",
        "JSON payload": '{"hostname": "prod-srv-042", "metrics": {"cpu": 92.3, "memory_gb": 28.1, "disk_io_mbps": 450}}',
    }
    selected = st.selectbox("Sample texts:", list(sample_texts.keys()))
    text_input = st.text_area("Text:", value=sample_texts[selected], height=120)

    if text_input:
        tokens = enc.encode(text_input)
        token_strings = [enc.decode([t]) for t in tokens]

        st.metric("Token Count", len(tokens))
        st.metric("Characters", len(text_input))
        st.metric("Ratio (chars/token)", f"{len(text_input)/max(len(tokens),1):.1f}")

        st.subheader("Token Breakdown")
        # Color-coded token visualization
        colors = ["#FFE0B2", "#B3E5FC", "#C8E6C9", "#F8BBD0", "#D1C4E9", "#FFECB3", "#B2DFDB", "#FFCDD2"]
        html_parts = []
        for i, ts in enumerate(token_strings):
            bg = colors[i % len(colors)]
            escaped = ts.replace("<", "&lt;").replace(">", "&gt;").replace(" ", "·").replace("\n", "↵")
            html_parts.append(f'<span style="background:{bg};padding:2px 4px;margin:1px;border-radius:3px;font-family:monospace;font-size:13px;" title="Token ID: {tokens[i]}">{escaped}</span>')
        st.markdown("".join(html_parts), unsafe_allow_html=True)

        with st.expander("Raw token IDs"):
            st.code(str(tokens))

with col2:
    st.subheader("Context Window Sizes")
    st.markdown("*How much text fits in one LLM call*")

    for model, ctx in CONTEXT_WINDOWS.items():
        pct = min(len(tokens) / ctx * 100, 100) if text_input else 0
        st.markdown(f"**{model}** — {ctx:,} tokens")
        st.progress(pct / 100, text=f"{pct:.4f}% used")

    st.divider()
    st.subheader("💡 Key Insight for Server Mgmt")
    st.info("""
    **Why this matters:**
    - A typical log file snippet = 500-2000 tokens
    - A full Kubernetes pod describe = 3000-8000 tokens
    - A full day of server metrics = 50000+ tokens

    Modern models (200K+ context) can process
    entire incident reports in one call.
    """)

    st.subheader("🧮 Cost Estimation")
    if text_input:
        token_count = len(tokens)
        st.markdown(f"""
        | Provider | Input Cost | For {token_count} tokens |
        |----------|-----------|------------------------|
        | GPT-4o | $2.50/1M | ${token_count * 2.5 / 1_000_000:.6f} |
        | Claude Sonnet | $3.00/1M | ${token_count * 3.0 / 1_000_000:.6f} |
        | Gemini 2.5 Pro | $1.25/1M | ${token_count * 1.25 / 1_000_000:.6f} |
        """)

st.divider()
st.markdown("**Takeaway:** Tokens ≠ words. Code and non-English text are less efficient. Context windows determine how much an LLM can 'see' at once.")
