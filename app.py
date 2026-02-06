from flask import Flask, render_template, request, jsonify
import pandas as pd
import sqlite3
import os
import uuid
from sentence_transformers import SentenceTransformer, util
from gtts import gTTS
import torch
import spacy

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
DATASET_PATH = os.path.join(BASE_DIR, "jb_data.db")
MODEL_DIR = os.path.join(BASE_DIR, "jb_semantic_model")

# Load semantic model
try:
    model = SentenceTransformer(MODEL_DIR)
    print("✅ Semantic model loaded.")
except Exception as e:
    print(f"⚠️ Could not load model: {e}")
    model = None

# Load dataset and embed
try:
    conn = sqlite3.connect(DATASET_PATH, check_same_thread=False)
    jb_data = pd.read_sql("SELECT * FROM jb_messages", conn).fillna("")
    jb_data["message"] = jb_data["message"].astype(str).str.strip().str.lower()
    corpus_embeddings = model.encode(
        jb_data["message"].tolist(),
        convert_to_tensor=True
    ) if model else None
    print("✅ Database loaded and embedded.")
except Exception as e:
    print(f"⚠️ Could not load database: {e}")
    jb_data, corpus_embeddings = None, None

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
    print("✅ spaCy model loaded.")
except Exception as e:
    print(f"⚠️ Could not load spaCy: {e}")
    nlp = None

def preserve_entities(user_text, system_text):
    if nlp is None:
        return system_text

    user_doc = nlp(user_text)
    sys_doc = nlp(system_text)

    replacements = {s_ent.text: u_ent.text for u_ent in user_doc.ents for s_ent in sys_doc.ents if s_ent.label_ == u_ent.label_}
    for old, new in replacements.items():
        system_text = system_text.replace(old, new)
    return system_text

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/process", methods=["POST"])
def process():
    data = request.json
    user_text = data.get("text", "").strip()
    action = data.get("action")
    lang = data.get("lang")

    if not user_text:
        return jsonify({"result": "Please enter a message."})

    if model is None or jb_data is None or corpus_embeddings is None:
        return jsonify({"result": "⚠️ Model or dataset not loaded."})

    query_emb = model.encode(user_text.lower(), convert_to_tensor=True)
    hits = util.semantic_search(query_emb, corpus_embeddings, top_k=1)
    best_idx = hits[0][0]["corpus_id"]
    best_score = hits[0][0]["score"]

    if best_score < 0.55:
        return jsonify({"result": f"No close dataset info for '{user_text}'. Try rephrasing."})

    matched_row = jb_data.iloc[best_idx]

    result = "Invalid action."
    if action == "simplify":
        result = matched_row.get("sim_msg", "Simplified version not available.")
    elif action == "translate":
        if lang in ["Tamil", "Hindi"]:
            result = matched_row.get(lang.lower(), "Translation not available.")
        else:
            result = "Unsupported language for translation."
    elif action == "what_next":
        lang_key = {"English": "wn_eng", "Tamil": "wn_tam", "Hindi": "wn_hin"}.get(lang)
        result = matched_row.get(lang_key, "What Next not available.") if lang_key else "Unsupported language for What Next."

    final_result = preserve_entities(user_text, result)
    return jsonify({"result": final_result})

@app.route("/voice", methods=["POST"])
def voice():
    data = request.json
    text = data.get("text", "").strip()

    if not text:
        return jsonify({"audio_url": ""})

    try:
        tts = gTTS(text=text, lang="en")
        filename = f"voice_{uuid.uuid4().hex}.mp3"
        file_path = os.path.join(STATIC_DIR, filename)
        tts.save(file_path)
        return jsonify({"audio_url": f"/static/{filename}"})
    except Exception as e:
        return jsonify({"audio_url": "", "error": str(e)})

if __name__ == "__main__":
    os.makedirs(STATIC_DIR, exist_ok=True)
    app.run(host="0.0.0.0", port=5000, debug=True)
