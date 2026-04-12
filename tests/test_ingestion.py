import re

# Tests for the ingestion pipeline: extractor and chunker outputs.
def test_extractor(chunks):
    """Tests raw extracted JSON: dict of {process_id: {table1, table2, table3}}."""
    errors = []
    KNOWN_GAPS = {"HWE.3": ["Process outcomes"]}

    for process_id, chunk in chunks.items():
        t1 = chunk.get("table1", {})
        for field in ["Process ID", "Process name", "Process purpose", "Process outcomes"]:
            if field not in t1 or not t1[field]:
                if field in KNOWN_GAPS.get(process_id, []):
                    print(f"[{process_id}] WARNING known gap: {field}")
                else:
                    errors.append(f"[{process_id}] table1 missing: {field}")
        if t1.get("Process ID") != process_id:
            errors.append(f"[{process_id}] table1 Process ID mismatch: {t1.get('Process ID')}")

        t2 = chunk.get("table2", [])
        if len(t2) == 0:
            errors.append(f"[{process_id}] table2 is empty")
        for i, bp in enumerate(t2):
            if not re.match(r'^[A-Z]+\.\d+\.BP\d+', bp):
                errors.append(f"[{process_id}] table2[{i}] bad BP format: {bp[:60]}")

        t3 = chunk.get("table3", {})
        if len(t3) == 0:
            errors.append(f"[{process_id}] table3 is empty")
        for key, outcomes in t3.items():
            if re.match(r'^BP\d+:', key) and len(outcomes) == 0:
                errors.append(f"[{process_id}] table3 BP missing outcome: {key}")
            if re.match(r'^\d{2}-\d{2}', key) and len(outcomes) == 0:
                errors.append(f"[{process_id}] table3 output item missing outcome: {key}")
            if re.match(r'^[A-Z]+\.\d+\s', key):
                errors.append(f"[{process_id}] table3 has title row as key: {key}")

    print(f"\n{'='*40}")
    print(f"[EXTRACTOR] Total processes: {len(chunks)}")
    print(f"[EXTRACTOR] Errors: {len(errors)}")
    if errors:
        for e in errors:
            print(f"  ✗ {e}")
    else:
        print("[EXTRACTOR] All tests passed.")
    if errors:
        raise ValueError(f"[EXTRACTOR] {len(errors)} errors found. Fix before continuing.")

# Tests for the chunker output: aspice_all_chunks.json, which contains all chunk types (chapter3/4/5).
def test_chunker(chunks):
    """Tests aspice_all_chunks.json — all chunk types (chapter3/4/5)."""
    errors = []
    common_fields = ["chunk_id", "source", "type", "title", "text", "page_number"]
    process_fields = ["process_name", "process_purpose", "outcomes", "base_practices", "output_items"]
    KNOWN_GAPS = {
    "HWE.3": ["outcomes"],
    "5.2": ["page_number"]
    }
    for chunk in chunks:
        cid = chunk.get("chunk_id", "<unknown>")

        for field in common_fields:
            if field not in chunk or chunk[field] is None:
                if field in KNOWN_GAPS.get(cid, []):
                    print(f"[{cid}] WARNING known gap: {field}")
                else:
                    errors.append(f"[{cid}] missing: {field}")

        if len(chunk.get("text", "")) < 50:
            errors.append(f"[{cid}] text too short")

        if chunk.get("type") == "process":
            for field in process_fields:
                if field not in chunk or not chunk[field]:
                    if field in KNOWN_GAPS.get(cid, []):
                       print(f"[{cid}] WARNING known gap: {field}")
                    else: 
                        errors.append(f"[{cid}] missing: {field}")
            if len(chunk.get("outcomes", [])) == 0:
                if "outcomes" in KNOWN_GAPS.get(cid, []):
                    print(f"[{cid}] WARNING known gap: outcomes")
                else:
                    errors.append(f"[{cid}] no outcomes")   
            if len(chunk.get("base_practices", [])) == 0:
                errors.append(f"[{cid}] no base practices")

    by_source = {}
    for c in chunks:
        by_source[c.get("source", "?")] = by_source.get(c.get("source", "?"), 0) + 1

    print(f"\n{'='*40}")
    print(f"[CHUNKER] Total chunks: {len(chunks)}")
    for src, count in sorted(by_source.items()):
        print(f"  {src}: {count} chunks")
    print(f"[CHUNKER] Errors: {len(errors)}")
    if errors:
        for e in errors:
            print(f"  ✗ {e}")
    else:
        print("[CHUNKER] All tests passed.")
    if errors:
        raise ValueError(f"[CHUNKER] {len(errors)} errors found. Fix before continuing.")
    
# Tests for chunk lengths: ensure no chunk exceeds token limits
def test_chunk_lengths(chunks, token_limit=8192):
    print(f"\n{'='*40}")
    print(f"[CHUNK LENGTHS] Token limit: {token_limit}")
    truncated = []
    for chunk in chunks:
        words = len(chunk['text'].split())
        tokens_approx = int(words * 1.3)
        status = "✓ OK" if tokens_approx <= token_limit else "❌ TRUNCATED"
        print(f"  {chunk['chunk_id']:<12} ~{tokens_approx:>5} tokens  {status}")
        if tokens_approx > token_limit:
            truncated.append(chunk['chunk_id'])
    print(f"\n[CHUNK LENGTHS] Truncated: {len(truncated)}")
    if truncated:
        raise ValueError(f"[CHUNK LENGTHS] {len(truncated)} chunks exceed token limit.")
