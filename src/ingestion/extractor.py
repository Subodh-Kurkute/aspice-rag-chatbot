import pdfplumber, re, json
from config import RAW_PDF, EXTRACTED_JSON

TABLE1_LABELS = ["Process ID", "Process name", "Process purpose", "Process outcomes"]

def extract_pdf_content(pdf_path, page_range=None):
    results = []
    with pdfplumber.open(pdf_path) as pdf:
        pages = pdf.pages[page_range[0]:page_range[1]] if page_range else pdf.pages
        for page in pages:
            results.append({
                "page_number": page.page_number,
                "tables": page.extract_tables()
            })
    return results

def is_new_subsection(table):
    for row in table:
        for cell in row:
            if cell and str(cell).strip() == "Process ID":
                return True
    return False

def get_process_id(table):
    for i, row in enumerate(table):
        for col in [1, 0]:
            if col < len(row) and str(row[col]).strip() == "Process ID":
                if i + 1 < len(table):
                    return str(table[i+1][col]).strip()
    return None

def parse_table1(table, last_label=None):
    data = {}
    current_label = last_label
    for row in table:
        val_col = None
        for col in [1, 0]:
            if col < len(row) and row[col] and str(row[col]).strip() in TABLE1_LABELS:
                val_col = col
                break
        if val_col is not None:
            current_label = str(row[val_col]).strip()
        elif current_label:
            value = next((str(c).strip() for c in row if c), None)
            if value:
                data[current_label] = value
                current_label = None
    return data, current_label

def parse_table2(table):
    has_header = 'Base Practices' in [str(c).strip() for c in table[0] if c]
    start = 1 if has_header else 0
    results = []
    for row in table[start:]:
        if not row[0]:
            continue
        cell = str(row[0]).strip()
        if re.match(r'^[A-Z]+\.\d+\.BP\d+|^BP\d+:', cell):
            results.append(cell)
        else:
            if results:
                results[-1] = results[-1] + ' ' + cell
    return results

def parse_table3(table, last_outcome_cols=None):
    results = {}
    header = table[0]
    outcome_cols = [i-1 for i, cell in enumerate(header)
                    if cell and 'emoctuO' in str(cell)]
    num_outcomes = len(outcome_cols) if outcome_cols else (
        len(last_outcome_cols) if last_outcome_cols else None
    )
    for row in table:
        first = str(row[0]).strip() if row[0] else ''
        if not first or 'emoctuO' in first:
            continue
        if re.match(r'^[A-Z]+\.\d+\s', first):
            continue
        if first in ['Output Information Items', 'Base Practices']:
            continue
        if outcome_cols:
            outcomes = [f"Outcome {i+1}" for i, col in enumerate(outcome_cols)
                       if col < len(row) and row[col] == 'X']
        elif num_outcomes:
            x_positions = [i for i, cell in enumerate(row[1:], 1) if cell == 'X']
            outcomes = []
            non_none_cols = [i for i, c in enumerate(row[1:], 1)
                            if c is not None and c != '']
            for x_pos in x_positions:
                if x_pos in non_none_cols:
                    rank = non_none_cols.index(x_pos)
                    if rank < num_outcomes:
                        outcomes.append(f"Outcome {rank+1}")
        else:
            outcomes = []
        results[first] = outcomes
    return results, outcome_cols if outcome_cols else last_outcome_cols

def assign_tables(table_buffer):
    result = {"table1": {}, "table2": [], "table3": {}}
    last_label = None
    last_outcome_cols = None
    for table in table_buffer:
        if is_new_subsection(table):
            parsed, last_label = parse_table1(table, last_label)
            result["table1"].update(parsed)
        elif len(table[0]) > 3:
            parsed, outcome_cols = parse_table3(table, last_outcome_cols)
            result["table3"].update(parsed)
            last_outcome_cols = outcome_cols
        else:
            has_bp = any(
                re.match(r'^[A-Z]+\.\d+\.BP\d+|^BP\d+:', str(row[0]).strip())
                for row in table if row[0]
            )
            if has_bp:
                result["table2"].extend(parse_table2(table))
            else:
                parsed, last_label = parse_table1(table, last_label)
                result["table1"].update(parsed)
    return result

def build_chunks(pdf_path=RAW_PDF, page_range=(29, 98)):
    chunks = {}
    current_subsection = None
    current_page = None
    table_buffer = []
    for page_data in extract_pdf_content(pdf_path, page_range):
        for table in page_data["tables"]:
            if is_new_subsection(table):
                if current_subsection and table_buffer:
                    chunk = assign_tables(table_buffer)
                    chunk["page_number"] = current_page
                    chunks[current_subsection] = chunk
                current_subsection = get_process_id(table)
                current_page = page_data["page_number"]
                table_buffer = [table]
            elif current_subsection:
                table_buffer.append(table)
    if current_subsection and table_buffer:
        chunk = assign_tables(table_buffer)
        chunk["page_number"] = current_page
        chunks[current_subsection] = chunk
    return chunks

def save_extracted(chunks, output_path=EXTRACTED_JSON):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(chunks, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(chunks)} processes to {output_path}")


def extract_text(pdf_path=RAW_PDF, page_range=None):
    with pdfplumber.open(pdf_path) as pdf:
        pages = pdf.pages[page_range[0]:page_range[1]] if page_range else pdf.pages
        return "\n".join(
            page.extract_text() for page in pages
            if page.extract_text()
        )


def extract_text_with_page_markers(pdf_path=RAW_PDF, page_range=None):
    """Returns text with <<<PAGE:N>>> markers so chunkers can recover page numbers."""
    with pdfplumber.open(pdf_path) as pdf:
        pages = pdf.pages[page_range[0]:page_range[1]] if page_range else pdf.pages
        parts = []
        for page in pages:
            text = page.extract_text()
            if text:
                parts.append(f"<<<PAGE:{page.page_number}>>>\n{text}")
        return "\n".join(parts)