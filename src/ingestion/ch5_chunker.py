import pdfplumber, re, json
from config import RAW_PDF, CH5_CHUNKS_JSON
from src.ingestion.extractor import extract_text_with_page_markers

def _extract_page_number(text):
    match = re.search(r'<<<PAGE:(\d+)>>>', text)
    return int(match.group(1)) if match else None

def _strip_markers(text):
    return re.sub(r'<<<PAGE:\d+>>>\n?', '', text)

def chunk_ch5():

    full_text_ch5 = extract_text_with_page_markers(RAW_PDF, (98, 117))

    sections = re.split(r'(?=\n5\.[1-6]\.[^\d])', full_text_ch5)

    chunks = []
    for section in sections:
        heading = re.match(r'\n?(?:<<<PAGE:\d+>>>\n)?(5\.\d+)\.\s+(.*?)(?:\n|$)', section)
        page_number = _extract_page_number(section)
        clean_text = _strip_markers(section).strip()
        chunks.append({
            "chunk_id": heading.group(1) if heading else "5.0",
            "source":   "chapter5",
            "type":     "annex",
            "title":    heading.group(2).strip() if heading else "Chapter 5 Introduction",
            "page_number": page_number,
            "text":     clean_text
        })

    print(f"Total chunks: {len(chunks)}")
    for c in chunks:
        print(c['chunk_id'], '|', c['title'][:60], '|', len(c['text']), 'chars')

    CH5_CHUNKS_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(CH5_CHUNKS_JSON, "w") as f:
        json.dump(chunks, f, indent=2)
        
    return chunks