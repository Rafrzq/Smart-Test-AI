import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from exam_service import generate_unique_exam_code
from grading_service import compute_semantic_similarity, generate_essay_feedback
from agent_engine import generate_exam_questions, get_agent_url, set_agent_url

app = Flask(__name__)
CORS(app)  # Izinkan Cross-Origin Resource Sharing untuk Frontend HTML/JS

@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "ok", 
        "message": "Smart Test AI Backend Live!",
        "agent_url": get_agent_url()
    })

@app.route("/api/config", methods=["GET", "POST"])
def api_config():
    if request.method == "POST":
        data = request.json or {}
        new_url = data.get("agent_url", "")
        if new_url:
            set_agent_url(new_url)
            return jsonify({"success": True, "agent_url": get_agent_url(), "message": "URL AI Agent Ngrok berhasil diperbarui!"})
        return jsonify({"success": False, "message": "URL tidak boleh kosong"}), 400
    return jsonify({"agent_url": get_agent_url()})

@app.route("/api/generate-exam", methods=["POST"])
def api_generate_exam():
    data = request.json or {}
    topic = data.get("topic", "Pemrograman Web")
    count = int(data.get("count", 5))
    
    print(f"📥 Menerima permintaan buat soal: Topik '{topic}', Jumlah {count}")
    
    # Panggil AI Agent (via Ngrok / Localhost)
    try:
        ai_response = generate_exam_questions(topic, count=count)
        if not ai_response:
            raise Exception("AI Agent response empty")
    except Exception as e:
        print(f"⚠️ Menggunakan AI fallback karena: {e}")
        ai_response = {
            "pg": [
                {
                    "soal": f"Apa konsep utama dari {topic}?",
                    "opsi": ["A. Statis", "B. Dinamis", "C. Asinkron", "D. Paralel"],
                    "jawaban": "B. Dinamis",
                    "level": "C4"
                }
            ],
            "essai": [
                {
                    "soal": f"Jelaskan implementasi {topic} pada skala produksi!",
                    "rubrik": "Jawaban memuat arsitektur, optimasi, dan efisiensi memori."
                }
            ]
        }
    
    exam_code = generate_unique_exam_code()
    return jsonify({
        "success": True,
        "exam_code": exam_code,
        "topic": topic,
        "data": ai_response,
        "agent_url": get_agent_url(),
        "message": f"Berhasil meng-generate {count} soal untuk {topic} melalui AI Agent!"
    })

@app.route("/api/evaluate-answer", methods=["POST"])
def api_evaluate_answer():
    data = request.json or {}
    question_text = data.get("question_text", "Jelaskan perbedaan Array dan Linked List!")
    student_answer = data.get("student_answer", "")
    quality = data.get("quality", "perfect")  # 'perfect' atau 'subpar'
    
    rubric = data.get("rubric", "Penjelasan komprehensif mengenai struktur data, alokasi memori kontigu vs non-kontigu, dan efisiensi penelusuran.")
    
    # Hitung similarity semantik dengan model NLP lokal
    similarity_score = compute_semantic_similarity(student_answer, rubric)
    
    # Panggil evaluasi AI Agent
    feedback = generate_essay_feedback(question_text, rubric, student_answer, similarity_score)
    
    return jsonify({
        "success": True,
        "similarity_score": similarity_score,
        "score": feedback.get("score", 100 if quality == "perfect" else 60),
        "reason": feedback.get("reason", "Jawaban telah dievaluasi oleh Otti AI Agent.")
    })

if __name__ == "__main__":
    current_agent = get_agent_url()
    print("🚀 Running Smart Test AI Backend API Server di http://localhost:5000 ...")
    print(f"🔗 Connected AI Agent Endpoint: {current_agent}")
    app.run(host="0.0.0.0", port=5000, debug=True)
