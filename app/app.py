import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import streamlit as st
from src.generation.generator import rag

st.title( "AI -Assistant for ASPICE")
st.markdown("""
**Ask me anything about ASPICE PAM 4.0.**  
Example questions:
- *What are the base practices of SWE.3?*
- *What work products does MAN.3 require?*
- *Explain capability level 2.*
""")

st.markdown("**Enter your query**")
query = st.text_input("Enter your query", label_visibility="hidden")

if st.button("Get Answer"):
    answer, retrieved, token_info = rag(query, top_k=2) 
    source = f"[Page{retrieved[0]['page_number']}]" if 'Not found in provided context' not in answer else None
    if source:
        st.write(f"**Source:** {source}")
    st.success(answer)
    with st.expander("Retrieved Chunks by RAG — Top 2 retrieved chunks"):
        for i, chunk in enumerate(retrieved, 1):
            st.markdown(f"**Chunk {i}**")
            st.markdown(f"📄 **ID:** `{chunk['chunk_id']}` | 📌 **Title:** {chunk['title']} | 📃 **Page:** {chunk['page_number']} | 🔢 **RRF:** `{chunk['rrf_score']:.4f}`")
            st.markdown(chunk['text'])
            st.divider()
    st.info(f"🔢 Prompt: {token_info['prompt_tokens']} | Completion: {token_info['completion_tokens']} | Total: {token_info['total_tokens']}")
    st.caption("⚠️ The RAG system uses Groq free tier which has token limits. Avoid rapid repeated queries.")
if st.button("Reset Conversation"):
    st.rerun()
