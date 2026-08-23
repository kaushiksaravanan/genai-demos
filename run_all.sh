#!/bin/bash
# Run all demos on consecutive ports
# Usage: ./run_all.sh        (launches all on ports 8501-8507)
#        ./run_all.sh 3      (launches only demo3)

DEMOS=(
    "app.py"
    "demo1_tokenization.py"
    "demo2_llm_interaction.py"
    "demo3_hallucinations.py"
    "demo4_react_agent.py"
    "demo5_langgraph.py"
    "demo6_mcp.py"
)

DIR="$(cd "$(dirname "$0")" && pwd)"
BASE_PORT=8501

if [ -n "$1" ]; then
    # Run single demo
    idx=$1
    port=$((BASE_PORT + idx))
    echo "Starting demo${idx} on port ${port}..."
    cd "$DIR" && python -m streamlit run "demo${idx}_"*.py --server.port "$port" --server.headless true
else
    # Run all
    echo "Starting all demos..."
    for i in "${!DEMOS[@]}"; do
        port=$((BASE_PORT + i))
        echo "  Port ${port}: ${DEMOS[$i]}"
        cd "$DIR" && python -m streamlit run "${DEMOS[$i]}" --server.port "$port" --server.headless true &
    done
    echo ""
    echo "All demos running. Press Ctrl+C to stop all."
    echo ""
    echo "  Launcher:       http://localhost:8501"
    echo "  Tokenization:   http://localhost:8502"
    echo "  LLM Interaction: http://localhost:8503"
    echo "  Hallucinations: http://localhost:8504"
    echo "  ReAct Agent:    http://localhost:8505"
    echo "  LangGraph:      http://localhost:8506"
    echo "  MCP:            http://localhost:8507"
    wait
fi
