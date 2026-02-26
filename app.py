"""
QIIME 2 Assistant - Interactive AI for QIIME 2 analysis questions.
Powered by Ollama (local LLM) with QIIME 2 manual as knowledge base.
"""

import os
import glob
import json
import requests
import streamlit as st


DOCS_DIR = os.path.join(os.path.dirname(__file__), "..", "qiime2-manual", "docs")
OLLAMA_URL = "http://localhost:11434"

CUSTOM_CSS = """
<style>
    /* 🐱 Hide Streamlit default chrome */
    #MainMenu, footer, header {visibility: hidden;}

    /* 🐱 Tighten top padding */
    .block-container {padding-top: 2rem;}

    /* 🐱 Welcome card styling */
    .welcome {
        text-align: center;
        padding: 2rem 0 1rem;
        color: #555;
    }
    .welcome h2 {
        font-size: 1.4rem;
        font-weight: 600;
        color: #333;
        margin-bottom: 0.3rem;
    }
    .welcome p {
        font-size: 0.95rem;
        color: #888;
    }

    /* 🐱 Example chips grid */
    .example-grid {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem;
        justify-content: center;
        padding: 0.5rem 0 2rem;
    }

    /* 🐱 Sidebar minimal */
    section[data-testid="stSidebar"] {
        width: 260px !important;
    }
    section[data-testid="stSidebar"] .stSelectbox label {
        font-size: 0.85rem;
    }
</style>
"""

EXAMPLES = [
    "DADA2のパラメータの決め方は？",
    "サンプリング深度はどう決める？",
    "内部標準（IS）の除去手順を教えて",
    "Rでphyloseqを使う方法は？",
    "PERMANOVAの実行方法は？",
    "分類器の作り方を教えて",
]

SYSTEM_PROMPT = """\
あなたはQIIME 2による16S rRNAアンプリコン解析の専門アシスタントです。
以下のマニュアルの内容に基づいて、ユーザーの質問に正確に回答してください。

## 回答のルール
- マニュアルに記載されている情報を優先して回答する
- コマンドを示す場合は、マニュアルに記載されたコマンドをそのまま引用する
- マニュアルに記載がない内容については、その旨を伝えた上で一般的な知識で補足する
- 日本語で回答する
- コードブロックを使ってコマンドを見やすく表示する
- R関連の質問にも対応する（マニュアルにR/phyloseqの章がある）

## マニュアル内容
{knowledge_base}
"""


@st.cache_data
def load_knowledge_base():
    """Load all markdown docs from qiime2-manual/docs/ as knowledge base."""
    docs = []
    md_files = sorted(glob.glob(os.path.join(DOCS_DIR, "*.md")))
    for filepath in md_files:
        filename = os.path.basename(filepath)
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        docs.append(f"--- {filename} ---\n{content}")
    return "\n\n".join(docs)


def get_available_models():
    """Fetch list of models from Ollama."""
    try:
        resp = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        resp.raise_for_status()
        return [m["name"] for m in resp.json().get("models", [])]
    except requests.RequestException:
        return []


def chat_stream(model, messages, knowledge_base):
    """Stream chat response from Ollama."""
    system = SYSTEM_PROMPT.format(knowledge_base=knowledge_base)
    payload = {
        "model": model,
        "messages": [{"role": "system", "content": system}] + messages,
        "stream": True,
    }
    with requests.post(
        f"{OLLAMA_URL}/api/chat", json=payload, stream=True, timeout=300
    ) as resp:
        resp.raise_for_status()
        for line in resp.iter_lines():
            if line:
                chunk = json.loads(line)
                token = chunk.get("message", {}).get("content", "")
                if token:
                    yield token


def main():
    st.set_page_config(
        page_title="QIIME 2 Assistant",
        page_icon="🧬",
        layout="centered",
    )
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

    # 🐱 Minimal sidebar
    with st.sidebar:
        st.markdown("#### Settings")
        models = get_available_models()
        if not models:
            st.error("Ollama が起動していません")
            st.caption("`ollama serve` を実行してください")
            st.stop()

        default_idx = 0
        for preferred in ["qwen2.5:7b", "qwen2.5-coder:7b"]:
            if preferred in models:
                default_idx = models.index(preferred)
                break

        model = st.selectbox("Model", models, index=default_idx, label_visibility="collapsed")

        if st.button("Clear chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

    # 🐱 Load knowledge base
    knowledge_base = load_knowledge_base()

    # 🐱 Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # 🐱 Welcome screen (shown when no messages)
    if not st.session_state.messages:
        st.markdown(
            '<div class="welcome">'
            "<h2>QIIME 2 Assistant</h2>"
            "<p>マニュアルに基づいてQIIME 2の疑問に回答します</p>"
            "</div>",
            unsafe_allow_html=True,
        )
        cols = st.columns(2)
        for i, ex in enumerate(EXAMPLES):
            with cols[i % 2]:
                if st.button(f"  {ex}", key=f"ex_{i}", use_container_width=True):
                    st.session_state["prefill"] = ex
                    st.rerun()

    # 🐱 Display chat history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # 🐱 Handle prefilled question
    prefill = st.session_state.pop("prefill", None)
    prompt = st.chat_input("質問を入力...")
    if prefill:
        prompt = prefill

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            api_messages = [
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ]
            response = st.write_stream(
                chat_stream(model, api_messages, knowledge_base)
            )

        st.session_state.messages.append({"role": "assistant", "content": response})


if __name__ == "__main__":
    main()
