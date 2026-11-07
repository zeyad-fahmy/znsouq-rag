"""ZNSouq support chat — run with:  streamlit run app.py"""
import os
os.environ.setdefault("HF_HUB_OFFLINE", "1")   # use the cached embedding model

import streamlit as st
from rag.answer import answer
from rag.orders import demo_customers

st.set_page_config(page_title="ZNSouq Support", page_icon="🛒")

# ---------- Sidebar: settings ----------
with st.sidebar:
    st.header("Settings")
    mode = st.radio("I am a...", ["buyer", "seller"], format_func=str.capitalize)
    k = st.slider("Chunks to retrieve (k)", min_value=2, max_value=8, value=4)
    show_sources = st.toggle("Show sources", value=True)
    customer_id = None
    if mode == "buyer":
        # Demo login: real apps get this from the signed-in account, never from the chat
        demos = demo_customers()
        pick = st.selectbox("Demo customer (logged in as)", demos,
                            format_func=lambda d: f"{d['customer_id']}: order {d['order_id']} ({d['status']})")
        customer_id = pick["customer_id"]
        st.caption(f"Try: Where is my order {pick['order_id']}?")
    if st.button("Clear chat"):
        st.session_state.messages = []
    st.divider()
    st.caption("Try asking:")
    examples = {
        "buyer": ["Can I return a shirt I already washed?",
                  "Do you deliver to Hurghada?",
                  "I bought headphones from Falcon Deals 10 days ago. Can I still return them?"],
        "seller": ["When do I get paid?",
                   "What is the referral fee for Electronics?",
                   "How long do I have to appeal a suspension?"],
    }
    for ex in examples[mode]:
        st.caption(f"• {ex}")


def render_sources(sources, search_query=None, tool_calls=None):
    with st.expander(f"Sources ({len(sources)})"):
        if search_query:
            st.caption(f"Searched for: {search_query}")
        for t in tool_calls or []:
            st.caption(f"🔧 Tool used: {t['tool']}({t['input'].get('order_id', '')}) → "
                       f"{'found' if t['output'].get('found') else 'not found'}")
        for i, h in enumerate(sources, 1):
            m = h["metadata"]
            st.markdown(f"**[{i}]** `{m['source']}` › {m['section']}  —  score {h['score']}")
            st.caption(h["text"][:300])


# ---------- Chat history ----------
st.title("🛒 ZNSouq Support")
st.caption(f"Answering as **{mode}** support · answers come only from ZNSouq's help center")
st.info("Demo project: ZNSouq is a fictional marketplace. Policies, stores and contact details are invented.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if show_sources and msg.get("sources"):
            render_sources(msg["sources"], msg.get("search_query"), msg.get("tool_calls"))

# ---------- New question ----------
if question := st.chat_input("Ask a question about ZNSouq..."):
    # The last few messages BEFORE this question = the conversation memory
    history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages[-6:]]
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Searching the help center..."):
            try:
                result = answer(question, mode=mode, k=k, history=history, customer_id=customer_id)
                reply, sources = result["answer"], result["sources"]
                search_query, tool_calls = result.get("search_query"), result.get("tool_calls")
            except Exception as e:
                reply, sources, search_query, tool_calls = f"Sorry, something went wrong: `{e}`", [], None, []
        st.markdown(reply)
        if show_sources and sources:
            render_sources(sources, search_query, tool_calls)

    st.session_state.messages.append({"role": "assistant", "content": reply, "sources": sources,
                                      "search_query": search_query, "tool_calls": tool_calls})
