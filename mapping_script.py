#!/usr/bin/env python3
# mapping_script.py
"""
Simple script to map Label-Studio style preannotations (JSONL) to OCR text files (.txt)
by fuzzy-matching span text inside OCR outputs. Minimal dependencies (stdlib only).
"""

import json
import os
import argparse
from difflib import SequenceMatcher

def normalize_text(s):
    return " ".join(s.split()).strip()

def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

def find_best_match_span(span_text, ocr_text, window_expansion=0.3):
    if not span_text or not ocr_text:
        return (None, None, 0.0)
    span_norm = normalize_text(span_text)
    ocr_norm = normalize_text(ocr_text)

    # direct find first (fast, exact)
    idx = ocr_norm.find(span_norm)
    if idx != -1:
        return (idx, idx + len(span_norm), 1.0)

    L = len(span_norm)
    if L == 0:
        return (None, None, 0.0)

    min_w = max(1, int(L * (1 - window_expansion)))
    max_w = min(len(ocr_norm), int(L * (1 + window_expansion)))
    best = (None, None, 0.0)
    stride = max(1, int(L/4))

    for w in range(min_w, max_w+1):
        for start in range(0, len(ocr_norm)-w+1, stride):
            chunk = ocr_norm[start:start+w]
            score = similarity(span_norm, chunk)
            if score > best[2]:
                best = (start, start+w, score)
                if score > 0.995:
                    return best
    return best

def map_predictions_to_ocr(labelstudio_jsonl_path, ocr_folder, output_path, doc_match_threshold=0.35):
    ls_docs = []
    with open(labelstudio_jsonl_path, 'r', encoding='utf8') as f:
        for line in f:
            if not line.strip():
                continue
            obj = json.loads(line)
            text = obj.get('data', {}).get('text', '')
            preds = []
            for p in obj.get('predictions', []):
                preds = p.get('result', [])
                break
            ls_docs.append({'raw': obj, 'text': text, 'preds': preds})

    ocr_texts = {}
    for fname in os.listdir(ocr_folder):
        if not fname.lower().endswith('.txt'):
            continue
        with open(os.path.join(ocr_folder, fname), 'r', encoding='utf8') as f:
            ocr_texts[fname] = f.read()

    mapped_results = []
    for i, doc in enumerate(ls_docs):
        ls_text = normalize_text(doc['text'])
        # find best OCR file by global similarity
        best_doc = (None, None)
        for fname, ocr_txt in ocr_texts.items():
            sim = similarity(ls_text, normalize_text(ocr_txt))
            if best_doc[0] is None or sim > best_doc[1]:
                best_doc = (fname, sim)

        match_fname, match_score = best_doc
        if match_score is None:
            match_score = 0.0

        if match_score < doc_match_threshold:
            print(f"WARNING: Low overall match for LS doc #{i+1} (best {match_fname} score={match_score:.3f}). Attempting per-span matching.")

        ocr_text = ocr_texts.get(match_fname, "")

        mapped_spans = []
        for pred in doc['preds']:
            v = pred.get('value', {})
            span_text = v.get('text', '')  # what Label-Studio stores as span text
            labels = v.get('labels', [])
            start, end, score = find_best_match_span(span_text, ocr_text)
            matched = ocr_text[start:end] if (start is not None and end is not None) else None
            mapped_spans.append({
                "orig_labelstudio": pred,
                "mapped_to_file": match_fname,
                "mapped_score": score,
                "mapped_start": start,
                "mapped_end": end,
                "mapped_text": matched,
                "labels": labels
            })

        mapped_results.append({
            "labelstudio_preview": ls_text[:200],
            "matched_file": match_fname,
            "match_score": match_score,
            "mapped_spans": mapped_spans
        })

    with open(output_path, 'w', encoding='utf8') as out:
        for r in mapped_results:
            out.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"Done. Results saved to: {output_path}")

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Map Label-Studio preannotations to OCR files")
    ap.add_argument("--labelstudio", required=True, help="Path to Label-Studio preannotated JSONL")
    ap.add_argument("--ocr_folder", required=True, help="Folder with OCR .txt files")
    ap.add_argument("--output", default="outputs/mapped_entities.jsonl", help="Output JSONL path")
    args = ap.parse_args()
    map_predictions_to_ocr(args.labelstudio, args.ocr_folder, args.output)
