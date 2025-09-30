#!/usr/bin/env python3
from flask import Flask, render_template, url_for
import json, os
from difflib import SequenceMatcher

BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE_DIR, "data")
OCR_DIR = os.path.join(DATA_DIR, "ocr_texts")
LS_PATH = os.path.join(DATA_DIR, "patta_labelstudio_preannotated.jsonl")

app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True

def normalize_text(s): return " ".join(s.split()).strip() if s else ""
def similarity(a,b): return SequenceMatcher(None, a, b).ratio() if a and b else 0.0

def find_best_match_span(span_text, ocr_text):
    if not span_text or not ocr_text: return (None, None, 0.0)
    span_norm, ocr_norm = normalize_text(span_text), normalize_text(ocr_text)
    idx = ocr_norm.find(span_norm)
    if idx != -1: return (idx, idx+len(span_norm), 1.0)
    return (None, None, 0.0)

def load_labelstudio_docs():
    docs = []
    if os.path.exists(LS_PATH):
        # use utf-8-sig to handle BOM safely
        with open(LS_PATH, 'r', encoding='utf-8-sig') as f:
            for line in f:
                if not line.strip():
                    continue
                obj = json.loads(line)
                text = obj.get('data', {}).get('text', '')
                preds = []
                for p in obj.get('predictions', []):
                    preds = p.get('result', [])
                    break
                docs.append({'text': text, 'preds': preds})
    return docs
def load_ocr_texts():
    texts = {}
    if os.path.exists(OCR_DIR):
        for fname in sorted(os.listdir(OCR_DIR)):
            if fname.lower().endswith('.txt'):
                with open(os.path.join(OCR_DIR, fname), 'r', encoding='utf-8-sig') as f:
                    texts[fname] = f.read()
    return texts


def map_doc_to_ocr(doc, ocr_texts):
    ls_text=normalize_text(doc['text'])
    best=(None,0.0)
    for fname,ocr in ocr_texts.items():
        sim=similarity(ls_text, normalize_text(ocr))
        if best[0] is None or sim>best[1]: best=(fname,sim)
    match_fname,match_score=best
    ocr_text=ocr_texts.get(match_fname,"")
    mapped_spans=[]
    for pred in doc['preds']:
        v=pred.get('value',{})
        span_text=v.get('text','')
        labels=v.get('labels',[])
        start,end,score=find_best_match_span(span_text,ocr_text)
        mapped_spans.append({
            "labels":labels,
            "span_text":span_text,
            "mapped_file":match_fname,
            "mapped_score":score,
            "mapped_text":ocr_text[start:end] if start!=None and end!=None else None
        })
    return {"preview":ls_text[:200],"matched_file":match_fname,"match_score":match_score,"spans":mapped_spans}

@app.route("/")
def index():
    docs=load_labelstudio_docs(); ocr_texts=load_ocr_texts()
    mapped=[dict(id=i+1,**map_doc_to_ocr(d,ocr_texts)) for i,d in enumerate(docs)]
    return render_template("index.html",mapped=mapped)

@app.route("/doc/<int:doc_id>")
def view_doc(doc_id):
    docs=load_labelstudio_docs(); ocr_texts=load_ocr_texts()
    if doc_id<1 or doc_id>len(docs): return "Document not found",404
    mapped=map_doc_to_ocr(docs[doc_id-1],ocr_texts)
    full_ocr=ocr_texts.get(mapped['matched_file'],"")
    return render_template("doc.html",doc_id=doc_id,mapped=mapped,ocr_text=full_ocr)

if __name__=="__main__": app.run(host="127.0.0.1",port=5000,debug=True)
