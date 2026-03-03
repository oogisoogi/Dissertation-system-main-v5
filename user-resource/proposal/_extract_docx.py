#!/usr/bin/env python3
"""Extract text from DOCX file using zipfile + xml.etree (no external dependencies)."""

import zipfile
import xml.etree.ElementTree as ET
import sys
import os

def extract_text_from_docx(docx_path):
    """Extract all text from a DOCX file."""
    # DOCX is a ZIP file containing XML
    with zipfile.ZipFile(docx_path, 'r') as z:
        # Main document content is in word/document.xml
        with z.open('word/document.xml') as f:
            tree = ET.parse(f)
            root = tree.getroot()

    # Define namespaces used in DOCX
    namespaces = {
        'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
        'wp': 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing',
    }

    paragraphs = []
    for para in root.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p'):
        texts = []
        for run in para.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}r'):
            for text in run.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t'):
                if text.text:
                    texts.append(text.text)
        if texts:
            paragraphs.append(''.join(texts))
        else:
            paragraphs.append('')  # Empty paragraph (line break)

    return '\n'.join(paragraphs)


def extract_tables_from_docx(docx_path):
    """Extract table content from a DOCX file."""
    with zipfile.ZipFile(docx_path, 'r') as z:
        with z.open('word/document.xml') as f:
            tree = ET.parse(f)
            root = tree.getroot()

    ns = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
    tables = []

    for tbl in root.iter(f'{{{ns}}}tbl'):
        table_rows = []
        for tr in tbl.iter(f'{{{ns}}}tr'):
            row_cells = []
            for tc in tr.iter(f'{{{ns}}}tc'):
                cell_texts = []
                for p in tc.iter(f'{{{ns}}}p'):
                    para_texts = []
                    for r in p.iter(f'{{{ns}}}r'):
                        for t in r.iter(f'{{{ns}}}t'):
                            if t.text:
                                para_texts.append(t.text)
                    cell_texts.append(''.join(para_texts))
                row_cells.append(' | '.join(cell_texts) if cell_texts else '')
            table_rows.append(' || '.join(row_cells))
        tables.append('\n'.join(table_rows))

    return tables


if __name__ == '__main__':
    docx_path = sys.argv[1] if len(sys.argv) > 1 else None
    if not docx_path:
        print("Usage: python _extract_docx.py <path_to_docx>")
        sys.exit(1)

    if not os.path.exists(docx_path):
        print(f"File not found: {docx_path}")
        sys.exit(1)

    # Extract main text
    text = extract_text_from_docx(docx_path)

    # Extract tables
    tables = extract_tables_from_docx(docx_path)

    # Output
    output_path = os.path.splitext(docx_path)[0] + '_extracted.txt'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("EXTRACTED TEXT FROM DOCX\n")
        f.write("=" * 80 + "\n\n")
        f.write(text)

        if tables:
            f.write("\n\n" + "=" * 80 + "\n")
            f.write("EXTRACTED TABLES\n")
            f.write("=" * 80 + "\n")
            for i, table in enumerate(tables, 1):
                f.write(f"\n--- Table {i} ---\n")
                f.write(table)
                f.write("\n")

    print(f"Text extracted to: {output_path}")
    print(f"Total paragraphs: {len(text.split(chr(10)))}")
    print(f"Total tables: {len(tables)}")
