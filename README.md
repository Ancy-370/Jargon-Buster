# Jargon Buster  
Government of India – Public Service Communication Tool

## 📌 Project Overview

Jargon Buster is a rule-based and semantic-assisted web application designed to simplify government messages for the general public. The system explains complex official text, translates it into regional languages, provides next-step guidance, and supports voice output for accessibility.

This project aims to bridge the communication gap between government services and citizens.

---

## 🚀 Features

- Simplification of government messages
- Translation to Tamil and Hindi
- Rule-based “What Next” guidance
- Voice output for better accessibility
- Semantic search using SentenceTransformer
- Database-backed structured responses
- Web-based interface using Flask

---

## 🧠 Technology Stack

- Frontend: HTML, CSS  
- Backend: Python (Flask)  
- NLP Model: all-MiniLM-L6-v2 (SentenceTransformer)  
- Database: SQLite  
- Libraries: scikit-learn, pandas, NumPy  
- Voice: Google Text-to-Speech  

---

## 🏗️ Project Structure

JarBus/
│
├── app.py
├── requirements.txt
├── JB_sheet.xlsx
├── jargon_buster.db
├── jb_semantic_model/
├── templates/
│ └── index.html
├── static/
│ └── voice_output.mp3
└── README.md

---

## ⚙ How to Run

1. Install dependencies:
	pip install -r requirements.txt

2. Run the application:
	python app.py

3. Open browser:
	http://localhost:5000

---

## 🚀 Future Enhancements

- Add Malayalam, Telugu, Kannada
- Convert into mobile app
- Integrate with government portals
- SMS-to-App redirection

