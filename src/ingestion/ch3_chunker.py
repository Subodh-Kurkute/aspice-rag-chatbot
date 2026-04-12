import pdfplumber, re, json
from config import RAW_PDF, CH3_CHUNKS_JSON
from src.ingestion.extractor import extract_text_with_page_markers

def _extract_page_number(text):
    """Return the first page number marker found in text, or None."""
    match = re.search(r'<<<PAGE:(\d+)>>>', text)
    return int(match.group(1)) if match else None

def _strip_markers(text):
    return re.sub(r'<<<PAGE:\d+>>>\n?', '', text)

def chunk_ch3():
    full_text_ch3 = extract_text_with_page_markers(RAW_PDF, (14, 28))
    sections = re.split(r'(?=\n3\.[1-9]\.[^\d]|^3\.[1-9]\.[^\d])', full_text_ch3, flags=re.MULTILINE)
    chunks = []
    for section in sections:
        heading = re.match(r'\n?(?:<<<PAGE:\d+>>>\n)?(3\.\d+)\.\s+(.*?)(?:\n|$)', section)
        page_number = _extract_page_number(section)
        clean_text = _strip_markers(section).strip()
        chunks.append({
            "chunk_id": heading.group(1) if heading else "3.0",
            "source":   "chapter3",
            "type":     "overview",
            "title":    heading.group(2).strip() if heading else "Chapter 3 Introduction",
            "page_number": page_number,
            "text":     clean_text
        })
    chunks = [c for c in chunks if c['text'].strip()]

    def split_large_chunk(chunk, max_chars=8000):
        text = chunk['text']
        if len(text) <= max_chars:
            return [chunk]
        
        parts = []
        while len(text) > max_chars:
            # find last newline before max_chars
            split_at = text.rfind('\n', 0, max_chars)
            if split_at == -1:
                split_at = max_chars
            parts.append(text[:split_at].strip())
            text = text[split_at:].strip()
        if text:
            parts.append(text)
        
        return [
            {**chunk, "chunk_id": f"{chunk['chunk_id']}_{i}", "text": t}
            for i, t in enumerate(parts)
        ]
    
    final_chunks = []
    for c in chunks:
        final_chunks.extend(split_large_chunk(c))

    print(f"Total chunks: {len(final_chunks)}")
    for c in final_chunks:
        print(c['chunk_id'], '|', c['title'][:60], '|', len(c['text']), 'chars')

    CH3_CHUNKS_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(CH3_CHUNKS_JSON, "w") as f:
        json.dump(final_chunks, f, indent=2)

    return final_chunks