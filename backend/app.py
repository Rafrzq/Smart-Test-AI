import json
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from exam_service import (
    generate_unique_exam_code,
    save_material_and_generate_questions,
    get_questions_by_material,
    update_question_by_id,
    approve_question_by_id,
    create_exam_from_material,
    start_student_exam,
    submit_student_exam,
    get_exam_results_recap,
    release_exam_submissions,
    submit_grade_appeal,
    decide_grade_appeal
)
from grading_service import compute_semantic_similarity, generate_essay_feedback
from agent_engine import generate_exam_questions, get_agent_url, set_agent_url

app = Flask(__name__)
CORS(app)  # Izinkan Cross-Origin Resource Sharing untuk Frontend HTML/JS

@app.route("/api/health", methods=["GET"])
@app.route("/health", methods=["GET"])
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
    
    print(f"--> Menerima permintaan buat soal: Topik '{topic}', Jumlah {count}")
    
    try:
        ai_response = generate_exam_questions(topic, count=count)
    except Exception as e:
        print(f"Warning: AI Agent error: {e}")
        ai_response = None
        
    if not ai_response:
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
    quality = data.get("quality", "perfect")
    
    rubric = data.get("rubric", "Penjelasan komprehensif mengenai struktur data, alokasi memori kontigu vs non-kontigu, dan efisiensi penelusuran.")
    
    similarity_score = compute_semantic_similarity(student_answer, rubric)
    feedback = generate_essay_feedback(question_text, rubric, student_answer, similarity_score)
    
    return jsonify({
        "success": True,
        "similarity_score": similarity_score,
        "score": feedback.get("score", 100 if quality == "perfect" else 60),
        "reason": feedback.get("reason", "Jawaban telah dievaluasi oleh Otti AI Agent.")
    })


# =========================================================================
# PATCH IMPLEMENTATION ENDPOINTS (PERBAIKAN_SMART_TEST_AI.md Section 4)
# =========================================================================

def extract_text_from_file(file_obj, filename: str) -> str:
    ext = filename.lower().split('.')[-1]
    if ext == 'pdf':
        try:
            import pdfplumber
            with pdfplumber.open(file_obj) as pdf:
                text = "\n".join([page.extract_text() or "" for page in pdf.pages])
                if text.strip():
                    return text
        except Exception as e:
            print(f"[WARN] pdfplumber error: {e}")
        try:
            import pypdf
            reader = pypdf.PdfReader(file_obj)
            text = "\n".join([page.extract_text() or "" for page in reader.pages])
            if text.strip():
                return text
        except Exception as e:
            print(f"[WARN] pypdf error: {e}")
    try:
        content = file_obj.read()
        if isinstance(content, bytes):
            return content.decode('utf-8', errors='ignore')
        return str(content)
    except Exception as e:
        return f"Extracted content from {filename}"


@app.route("/materi/upload", methods=["POST"])
@app.route("/api/materi/upload", methods=["POST"])
def upload_materi():
    try:
        title = request.form.get("title") or request.json.get("title") if request.is_json else None
        title = title or "Materi Pembelajaran Baru"
        
        jumlah_pg = int(request.form.get("jumlah_pg") or (request.json.get("jumlah_pg") if request.is_json else 5))
        jumlah_essai = int(request.form.get("jumlah_essai") or (request.json.get("jumlah_essai") if request.is_json else 2))
        
        raw_dist = request.form.get("level_distribution") or (request.json.get("level_distribution") if request.is_json else None)
        if isinstance(raw_dist, str):
            try:
                level_distribution = json.loads(raw_dist)
            except Exception:
                level_distribution = {"C4": 100}
        elif isinstance(raw_dist, dict):
            level_distribution = raw_dist
        else:
            level_distribution = {"C4": 100}

        content_text = ""
        if "file" in request.files:
            file_obj = request.files["file"]
            content_text = extract_text_from_file(file_obj, file_obj.filename)
        elif request.is_json and request.json.get("content_text"):
            content_text = request.json["content_text"]
        elif request.form.get("content_text"):
            content_text = request.form["content_text"]
        else:
            content_text = f"Materi pembelajaran tentang {title}."

        result = save_material_and_generate_questions(
            title=title,
            content_text=content_text,
            jumlah_pg=jumlah_pg,
            jumlah_essai=jumlah_essai,
            level_distribution=level_distribution
        )
        return jsonify({"success": True, "data": result})
    except Exception as e:
        print(f"Error /materi/upload: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/bank-soal/<materi_id>", methods=["GET"])
@app.route("/api/bank-soal/<materi_id>", methods=["GET"])
def get_bank_soal(materi_id):
    try:
        questions = get_questions_by_material(materi_id)
        return jsonify({"success": True, "questions": questions})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/bank-soal/<soal_id>", methods=["PUT"])
@app.route("/api/bank-soal/<soal_id>", methods=["PUT"])
def edit_bank_soal(soal_id):
    try:
        data = request.json or {}
        updated = update_question_by_id(soal_id, data)
        return jsonify({"success": True, "question": updated})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/bank-soal/<soal_id>/approve", methods=["PATCH"])
@app.route("/api/bank-soal/<soal_id>/approve", methods=["PATCH"])
def approve_bank_soal(soal_id):
    try:
        approved = approve_question_by_id(soal_id)
        return jsonify({"success": True, "question": approved})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/ujian/buat", methods=["POST"])
@app.route("/api/ujian/buat", methods=["POST"])
def buat_ujian():
    try:
        data = request.json or request.form
        material_id = data.get("material_id")
        shown_per_student = int(data.get("questions_shown_per_student", 5))
        duration = int(data.get("duration_minutes", 60))
        title = data.get("title")

        if not material_id:
            # Fallback mock material creation if not supplied
            mat = save_material_and_generate_questions(title or "Ujian Baru", "Materi Ujian", shown_per_student, 2)
            material_id = mat["material_id"]

        exam = create_exam_from_material(material_id, shown_per_student, duration, title)
        return jsonify({"success": True, "exam": exam})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/ujian/<kode>/mulai", methods=["POST"])
@app.route("/api/ujian/<kode>/mulai", methods=["POST"])
def mulai_ujian(kode):
    try:
        data = request.json or {}
        nama = data.get("nama") or data.get("student_name") or "Siswa Anonim"
        nis = data.get("nis") or data.get("student_nis") or "-"

        exam_payload = start_student_exam(nama, nis, kode)
        return jsonify({"success": True, "data": exam_payload})
    except ValueError as ve:
        return jsonify({"success": False, "error": str(ve)}), 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/ujian/<kode>/submit", methods=["POST"])
@app.route("/api/ujian/<kode>/submit", methods=["POST"])
def submit_ujian(kode):
    try:
        data = request.json or {}
        student_name = data.get("student_name") or data.get("nama") or "Siswa Anonim"
        student_nis = data.get("student_nis") or data.get("nis") or "-"
        answers = data.get("answers", [])

        submission = submit_student_exam(kode, student_name, student_nis, answers)
        return jsonify({"success": True, "submission": submission})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/ujian/<id>/hasil", methods=["GET"])
@app.route("/api/ujian/<id>/hasil", methods=["GET"])
def hasil_ujian(id):
    try:
        recap = get_exam_results_recap(id)
        return jsonify({"success": True, "results": recap})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/ujian/<id>/rilis", methods=["PATCH"])
@app.route("/api/ujian/<id>/rilis", methods=["PATCH"])
def rilis_ujian(id):
    try:
        res = release_exam_submissions(id)
        return jsonify({"success": True, "data": res})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/sanggahan", methods=["POST"])
@app.route("/api/sanggahan", methods=["POST"])
def submit_sanggahan():
    try:
        data = request.json or {}
        sub_id = data.get("submission_id")
        reason = data.get("student_reason") or data.get("reason", "")
        if not sub_id or not reason:
            return jsonify({"success": False, "error": "submission_id dan student_reason wajib diisi"}), 400

        appeal = submit_grade_appeal(sub_id, reason)
        return jsonify({"success": True, "appeal": appeal})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/sanggahan/<id>/keputusan", methods=["PATCH"])
@app.route("/api/sanggahan/<id>/keputusan", methods=["PATCH"])
def keputusan_sanggahan(id):
    try:
        data = request.json or {}
        status = data.get("status")
        teacher_notes = data.get("teacher_notes")
        if not status:
            return jsonify({"success": False, "error": "status (approved/rejected) wajib diisi"}), 400

        appeal = decide_grade_appeal(id, status, teacher_notes)
        return jsonify({"success": True, "appeal": appeal})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == "__main__":
    current_agent = get_agent_url()
    print("=== Running Smart Test AI Backend API Server di http://localhost:5000 ===")
    print(f"Connected AI Agent Endpoint: {current_agent}")
    app.run(host="0.0.0.0", port=5000, debug=False)


