import json, re
from config import EXTRACTED_JSON, CHUNKS_JSON


def parse_outcomes(outcomes_str: str) -> list[str]:
    outcomes = []
    parts = re.split(r'\n?(\d+)\)', outcomes_str)
    parts = [p.strip() for p in parts if p.strip()]
    i = 0
    while i < len(parts):
        if parts[i].isdigit():
            num = int(parts[i])
            if i + 1 < len(parts):
                desc = parts[i + 1].replace('\n', ' ').strip()
                outcomes.append(f"Outcome {num}: {desc}")
                i += 2
        else:
            i += 1
    return outcomes


def parse_output_items(table3: dict) -> list[dict]:
    items = []
    for key, outcomes in table3.items():
        if not key.startswith("BP"):
            parts = key.strip().split(' ', 1)
            item_id = parts[0] if len(parts) > 1 else key
            name = parts[1] if len(parts) > 1 else key
            items.append({
                "item_id": item_id,
                "name": name.replace('\n', ' ').strip(),
                "required_for_outcomes": outcomes
            })
    return items


def parse_base_practices(process_id: str, table2: list, table3: dict) -> list[dict]:
    bp_outcome_map = {}
    for key, outcomes in table3.items():
        if key.startswith("BP"):
            match = re.match(r'BP(\d+)', key)
            if match:
                bp_outcome_map[match.group(1)] = outcomes

    bps = []
    for bp_text in table2:
        match = re.search(r'\.BP(\d+)', bp_text)
        if not match:
            match = re.search(r'BP(\d+)', bp_text)
        bp_num = match.group(1) if match else None
        bp_id_match = re.match(r'([A-Z]+\.\d+\.BP\d+)', bp_text)
        bp_id = bp_id_match.group(1) if bp_id_match else f"{process_id}.BP{bp_num}"
        bps.append({
            "bp_id": bp_id,
            "description": bp_text.replace('\n', ' ').strip(),
            "satisfies_outcomes": bp_outcome_map.get(bp_num, [])
        })
    return bps


def build_text(process_id, process_name, process_purpose, outcomes, base_practices, output_items) -> str:
    lines = []
    lines.append(f"{process_id} {process_name}.")
    lines.append(f"Purpose: {process_purpose.replace(chr(10), ' ')}")
    lines.append("\nOutcomes:")
    for o in outcomes:
        lines.append(o)
    lines.append("\nBase Practices:")
    for bp in base_practices:
        outcomes_str = ', '.join(bp['satisfies_outcomes'])
        lines.append(f"{bp['description']} Satisfies {outcomes_str}.")
    lines.append("\nOutput Items and Evidence:")
    for item in output_items:
        outcomes_str = ', '.join(item['required_for_outcomes'])
        lines.append(f"{item['item_id']} {item['name']} — required for {outcomes_str}.")
    return '\n'.join(lines)


def chunk_processes(input_path=EXTRACTED_JSON, output_path=CHUNKS_JSON) -> list[dict]:
    """Chunks pages 29-98 (process definitions: table1/table2/table3 structure)."""
    with open(input_path, 'r', encoding='utf-8-sig') as f:
        data = json.load(f)

    chunks = []
    for process_id, process_data in data.items():
        t1 = process_data['table1']
        t2 = process_data['table2']
        t3 = process_data['table3']

        outcomes = parse_outcomes(t1.get('Process outcomes', ''))
        base_practices = parse_base_practices(process_id, t2, t3)
        output_items = parse_output_items(t3)

        text = build_text(
            process_id=process_id,
            process_name=t1['Process name'],
            process_purpose=t1['Process purpose'],
            outcomes=outcomes,
            base_practices=base_practices,
            output_items=output_items
        )

        chunks.append({
            "chunk_id": process_id,
            "source": "chapter4",
            "type": "process",
            "title": t1['Process name'],
            "process_name": t1['Process name'],
            "process_purpose": t1['Process purpose'].replace('\n', ' '),
            "page_number": process_data.get("page_number"),
            "outcomes": outcomes,
            "base_practices": base_practices,
            "output_items": output_items,
            "text": text
        })

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(chunks, f, indent=2, ensure_ascii=False)
        print(f"Saved {len(chunks)} chunks to {output_path}")

    return chunks