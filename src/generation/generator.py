from src.retrieval.hybrid import hybrid_search
from src.generation.client import get_groq_client, GROQ_MODEL

groq_client = get_groq_client()
USE_HYDE = False  # Toggle here

SYSTEM_PROMPT = """You are an ASPICE process guidance assistant.
Answer ONLY using the provided context. 
If no relevant information exists, say 'Not found in provided context'."""

HYDE_PROMPT = """Write a short, factual paragraph that would answer this question 
about ASPICE PAM 4.0 processes. Be concise and technical."""

def generate_hypothetical_doc(query_text):
    """HyDE: generate a hypothetical answer to improve retrieval embedding."""
    response = groq_client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {'role': 'system', 'content': HYDE_PROMPT},
            {'role': 'user',   'content': query_text}
        ],
        temperature=0.0,
        max_tokens=200
    )
    return response.choices[0].message.content


def build_context(retrieved_chunks, max_chars=5000):
    lines = []
    for i, r in enumerate(retrieved_chunks, 1):
        text = r['text'][:max_chars]   
        lines.append(f"[{i}] chunk_id: {r['chunk_id']}\ntitle: {r['title']}\n{text}")
    return '\n\n'.join(lines)


def rag(query_text, top_k=5):
    retrieval_query = query_text
    if USE_HYDE:
        retrieval_query = generate_hypothetical_doc(query_text)
        print(f"[HyDE] Hypothetical doc:\n{retrieval_query[:200]}...\n")

    # 1. Retrieve
    retrieved = hybrid_search(retrieval_query, top_k=top_k)
    context   = build_context(retrieved)
    
    # 2. Generate
    user_msg = f"Context:\n{context}\n\nQuestion: {query_text}"
    response = groq_client.chat.completions.create(
    model=GROQ_MODEL,
    messages=[
        {'role': 'system', 'content': SYSTEM_PROMPT},
        {'role': 'user',   'content': user_msg}
    ],
    temperature=0.0,
    max_tokens=512
    )
    answer = response.choices[0].message.content
    DIVIDER = "-" * 60   
    # 3. Display
    if 'Not found in provided context' not in answer:
        print(f"\n{DIVIDER}")
        sources = f"[Page{retrieved[0]['page_number']}]"
        print(f"Question:  \n{query_text}")
        print(f"Answer:\n{answer}\n Source: {sources}")
        print('\nRetrieved chunks:')
        for r in retrieved:
            print(f"  {r['chunk_id']} | {r['title']} | rrf={r['rrf_score']}")
        print(f"\n{DIVIDER}")
    else:
        print(f"\n{DIVIDER}")
        print(f"Question:  \n{query_text}")
        print(f"Answer:\n{answer}")
        print(f"\n{DIVIDER}")
    # Token usage
    usage = response.usage
    token_info = {
    "prompt_tokens": usage.prompt_tokens,
    "completion_tokens": usage.completion_tokens,
    "total_tokens": usage.total_tokens
    }
    print(f"Prompt tokens:     {usage.prompt_tokens}")
    print(f"Response tokens: {usage.completion_tokens}")
    print(f"Total tokens:      {usage.total_tokens}")
    
    return answer, retrieved, token_info
    