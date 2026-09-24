import random
import string
import json
from typing import Dict, Any, Optional, List
from agent_engine import generate_exam_questions
from services.ai_client import generate_questions as generate_ai_text
from grading_service import grade_essay_draft
from test_db import get_supabase_client


def generate_unique_exam_code(length: int = 6) -> str:
    """Fungsi helper untuk membuat kode unik ujian acak (contoh: MATH99)."""
    characters = string.ascii_uppercase + string.digits
    return "".join(random.choices(characters, k=length))


def save_exam_to_database(
    title: str, 
    teacher_name: str, 
    materi_text: str
) -> Optional[Dict[str, Any]]:
    """Fungsi utama untuk memproses materi lewat Gemini dan menyimpannya ke Supabase."""
    ai_response = generate_exam_questions(materi_text)
    if not ai_response:
        print("❌ ERROR: Gagal mendapatkan respon dari AI Agent.")
        return None

    try:
        supabase = get_supabase_client()
        exam_code = generate_unique_exam_code()

        exam_payload = {
            "exam_code": exam_code,
            "title": title,
            "teacher_name": teacher_name
        }
        
        exam_res = supabase.table("exams").insert(exam_payload).execute()
        
        if not exam_res.data:
            raise Exception("Gagal memasukkan data ke tabel exams.")

        exam_id = exam_res.data[0]["id"]
        print(f"✅ Header Ujian Berhasil Dibuat! Exam ID: {exam_id} | Kode: {exam_code}")

        questions_to_insert: List[Dict[str, Any]] = []

        for pg_item in ai_response.get("pg", []):
            questions_to_insert.append({
                "exam_id": exam_id,
                "question_type": "pg",
                "question_text": pg_item.get("soal", ""),
                "options": pg_item.get("opsi", []),
                "correct_answer": pg_item.get("jawaban", ""),
                "difficulty_level": pg_item.get("level", "C4")
            })

        for essai_item in ai_response.get("essai", []):
            questions_to_insert.append({
                "exam_id": exam_id,
                "question_type": "essai",
                "question_text": essai_item.get("soal", ""),
                "correct_answer": "Sesuai Rubrik",
                "rubric_essay": essai_item.get("rubrik", ""),
                "difficulty_level": "C4"
            })

        questions_res = supabase.table("questions").insert(questions_to_insert).execute()
        
        print(f"✅ Berhasil Menyimpan {len(questions_res.data)} Soal ke Database Supabase!")

        return {
            "exam_id": exam_id,
            "exam_code": exam_code,
            "total_questions": len(questions_res.data)
        }

    except Exception as err:
        print(f"❌ ERROR Transaksi Database: {err}")
        return None


def save_material_and_generate_questions(
    title: str,
    content_text: str,
    jumlah_pg: int = 5,
    jumlah_essai: int = 2,
    level_distribution: Any = None,
    teacher_id: Optional[str] = None
) -> Dict[str, Any]:
    supabase = get_supabase_client()
    
    # 1. Insert material (status: processing) with graceful fallback for column differences
    mat_payload = {
        "title": title,
        "content_text": content_text,
        "jumlah_pg": jumlah_pg,
        "jumlah_essai": jumlah_essai,
        "level_distribution": level_distribution if level_distribution else {"C4": 100},
        "status": "processing"
    }
    if teacher_id:
        mat_payload["teacher_id"] = teacher_id

    material_id = None
    try:
        mat_res = supabase.table("materials").insert(mat_payload).execute()
        if mat_res.data:
            material_id = mat_res.data[0]["id"]
    except Exception as e:
        print(f"[WARN] Full material insert failed ({e}), retrying with minimal payload...")
        try:
            minimal_payload = {"title": title}
            mat_res = supabase.table("materials").insert(minimal_payload).execute()
            if mat_res.data:
                material_id = mat_res.data[0]["id"]
        except Exception as e2:
            print(f"[WARN] Minimal material insert also failed ({e2}), generating fallback UUID...")
            import uuid
            material_id = str(uuid.uuid4())

    if not material_id:
        import uuid
        material_id = str(uuid.uuid4())

    # 2. Call AI Agent
    instruction = (
        f"Buatkan {jumlah_pg} soal pilihan ganda (PG) dan {jumlah_essai} soal esai "
        f"dari materi berikut. Distribusi level: {json.dumps(level_distribution or {})}. "
        "Format JSON murni: {\"pg\": [{\"soal\":\"...\",\"opsi\":[\"A...\",\"B...\",\"C...\",\"D...\"],\"jawaban\":\"A...\",\"level\":\"C4\"}], \"essai\": [{\"soal\":\"...\",\"rubrik\":\"...\"}]}"
    )
    
    ai_questions = None
    try:
        raw_res = generate_ai_text(instruction, content_text)
        if isinstance(raw_res, str):
            clean = raw_res.strip()
            if clean.startswith("```json"): clean = clean[7:]
            if clean.startswith("```"): clean = clean[3:]
            if clean.endswith("```"): clean = clean[:-3]
            ai_questions = json.loads(clean.strip())
        elif isinstance(raw_res, dict):
            ai_questions = raw_res
    except Exception as e:
        print(f"[WARN] ai_client call error, falling back to agent_engine: {e}")
        ai_questions = generate_exam_questions(content_text, count=jumlah_pg)

    if not ai_questions or not isinstance(ai_questions, dict):
        ai_questions = generate_exam_questions(content_text, count=jumlah_pg)

    # 3. Save draft questions
    questions_to_insert = []

    for pg in ai_questions.get("pg", []):
        questions_to_insert.append({
            "material_id": material_id,
            "question_type": "pg",
            "question_text": pg.get("soal", ""),
            "options": pg.get("opsi", []),
            "correct_answer": pg.get("jawaban", ""),
            "difficulty_level": pg.get("level", "C4"),
            "status": "draft"
        })

    for es in ai_questions.get("essai", []):
        questions_to_insert.append({
            "material_id": material_id,
            "question_type": "essai",
            "question_text": es.get("soal", ""),
            "rubric_essay": es.get("rubrik", ""),
            "correct_answer": es.get("rubrik", ""),
            "difficulty_level": "C4",
            "status": "draft"
        })

    if questions_to_insert:
        try:
            q_res = supabase.table("questions").insert(questions_to_insert).execute()
            inserted_questions = q_res.data or []
        except Exception as e:
            print(f"[WARN] Batch insert questions failed ({e}), inserting items with basic schema...")
            inserted_questions = []
            for q_item in questions_to_insert:
                try:
                    basic_q = {
                        "question_type": q_item["question_type"],
                        "question_text": q_item["question_text"],
                        "options": q_item.get("options", []),
                        "correct_answer": q_item.get("correct_answer", ""),
                        "status": "draft"
                    }
                    res_q = supabase.table("questions").insert(basic_q).execute()
                    if res_q.data:
                        inserted_questions.append(res_q.data[0])
                except Exception as e2:
                    print(f"[WARN] Individual question insert error: {e2}")
                    # Local fallback item for UI edit
                    import uuid
                    q_item["id"] = str(uuid.uuid4())
                    inserted_questions.append(q_item)
    else:
        inserted_questions = []

    # 4. Update material status if possible
    try:
        supabase.table("materials").update({"status": "generated"}).eq("id", material_id).execute()
    except Exception as e:
        print(f"[WARN] Update material status skipped: {e}")

    return {
        "material_id": material_id,
        "title": title,
        "status": "generated",
        "questions_count": len(inserted_questions),
        "questions": inserted_questions
    }


def get_questions_by_material(material_id: str) -> List[Dict[str, Any]]:
    supabase = get_supabase_client()
    res = supabase.table("questions").select("*").eq("material_id", material_id).execute()
    return res.data or []


def update_question_by_id(soal_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
    supabase = get_supabase_client()
    allowed = ["question_text", "options", "correct_answer", "rubric_essay", "difficulty_level", "status"]
    update_data = {k: v for k, v in data.items() if k in allowed}
    res = supabase.table("questions").update(update_data).eq("id", soal_id).execute()
    if res.data:
        return res.data[0]
    raise Exception(f"Soal dengan ID {soal_id} tidak ditemukan.")


def approve_question_by_id(soal_id: str) -> Dict[str, Any]:
    return update_question_by_id(soal_id, {"status": "approved"})


def create_exam_from_material(
    material_id: str,
    questions_shown_per_student: int = 5,
    duration_minutes: int = 60,
    title: Optional[str] = None
) -> Dict[str, Any]:
    supabase = get_supabase_client()
    exam_code = generate_unique_exam_code()

    if not title:
        mat_res = supabase.table("materials").select("title").eq("id", material_id).execute()
        title = mat_res.data[0]["title"] if mat_res.data else f"Ujian {exam_code}"

    exam_payload = {
        "material_id": material_id,
        "title": title,
        "exam_code": exam_code,
        "duration_minutes": duration_minutes,
        "questions_shown_per_student": questions_shown_per_student,
        "status": "active"
    }

    res = supabase.table("exams").insert(exam_payload).execute()
    if not res.data:
        raise Exception("Gagal membuat ujian baru.")

    exam = res.data[0]
    return {
        "exam_id": exam["id"],
        "exam_code": exam["exam_code"],
        "title": exam["title"],
        "duration_minutes": exam["duration_minutes"],
        "questions_shown_per_student": exam["questions_shown_per_student"]
    }


def start_student_exam(nama: str, nis: str, exam_code: str) -> Dict[str, Any]:
    supabase = get_supabase_client()
    # Check exam existence & status
    exam_res = supabase.table("exams").select("*").eq("exam_code", exam_code).eq("status", "active").execute()
    if not exam_res.data:
        raise ValueError(f"Kode Ujian '{exam_code}' tidak ditemukan atau tidak aktif.")

    exam = exam_res.data[0]
    exam_id = exam["id"]
    n_questions = exam.get("questions_shown_per_student", 5)

    # Get approved questions for this exam or material
    q_res = supabase.table("questions").select("*").or_(f"exam_id.eq.{exam_id},material_id.eq.{exam.get('material_id')}").eq("status", "approved").execute()
    all_questions = q_res.data or []

    if not all_questions:
        # Fallback: get any questions for exam or material
        q_res = supabase.table("questions").select("*").or_(f"exam_id.eq.{exam_id},material_id.eq.{exam.get('material_id')}").execute()
        all_questions = q_res.data or []

    # Shuffle and pick N
    random.shuffle(all_questions)
    selected_questions = all_questions[:n_questions]

    sanitized_questions = []
    for q in selected_questions:
        q_copy = dict(q)
        # Remove correct answer from student payload
        q_copy.pop("correct_answer", None)
        q_copy.pop("rubric_essay", None)

        # Shuffle options for PG if available
        if q_copy.get("question_type") == "pg" and isinstance(q_copy.get("options"), list):
            opts = list(q_copy["options"])
            random.shuffle(opts)
            q_copy["options"] = opts

        sanitized_questions.append(q_copy)

    return {
        "exam_id": exam_id,
        "title": exam["title"],
        "duration_minutes": exam.get("duration_minutes", 60),
        "student_name": nama,
        "student_nis": nis,
        "questions": sanitized_questions
    }


def submit_student_exam(exam_code: str, student_name: str, student_nis: str, answers: List[Dict[str, Any]]) -> Dict[str, Any]:
    supabase = get_supabase_client()
    exam_res = supabase.table("exams").select("id").eq("exam_code", exam_code).execute()
    if not exam_res.data:
        raise ValueError(f"Kode Ujian '{exam_code}' tidak valid.")

    exam_id = exam_res.data[0]["id"]

    # Calculate PG and Essay scores
    pg_correct = 0
    total_pg = 0
    essay_scores = []

    for ans in answers:
        soal_id = ans.get("question_id")
        user_ans = ans.get("answer", "")
        
        q_data = None
        if soal_id:
            q_res = supabase.table("questions").select("*").eq("id", soal_id).execute()
            if q_res.data:
                q_data = q_res.data[0]

        if q_data:
            q_type = q_data.get("question_type", "pg")
            if q_type == "pg":
                total_pg += 1
                correct = q_data.get("correct_answer", "")
                if user_ans.strip().lower() == correct.strip().lower() or user_ans.strip().startswith(correct.strip()[:1]):
                    pg_correct += 1
            else:
                key = q_data.get("rubric_essay") or q_data.get("correct_answer") or ""
                eval_res = grade_essay_draft(user_ans, key)
                essay_scores.append(eval_res["skor_draft"])

    pg_score = (pg_correct / total_pg * 100) if total_pg > 0 else 0
    essay_draft_score = (sum(essay_scores) / len(essay_scores) * 25) if essay_scores else 0  # 1-4 scale converted to 100
    total_score = round((pg_score + essay_draft_score) / (2 if (total_pg > 0 and essay_scores) else 1), 2)

    sub_payload = {
        "exam_id": exam_id,
        "student_name": student_name,
        "student_nis": student_nis,
        "answers": answers,
        "pg_score": round(pg_score, 2),
        "essay_draft_score": round(essay_draft_score, 2),
        "total_score": total_score,
        "status": "pending_review"
    }

    sub_res = supabase.table("student_submissions").insert(sub_payload).execute()
    if not sub_res.data:
        raise Exception("Gagal menyimpan jawaban siswa.")

    submission = sub_res.data[0]
    return {
        "submission_id": submission["id"],
        "student_name": student_name,
        "pg_score": submission["pg_score"],
        "essay_draft_score": submission["essay_draft_score"],
        "total_score": submission["total_score"],
        "status": submission["status"]
    }


def get_exam_results_recap(exam_id: str) -> List[Dict[str, Any]]:
    supabase = get_supabase_client()
    res = supabase.table("student_submissions").select("*").eq("exam_id", exam_id).execute()
    return res.data or []


def release_exam_submissions(exam_id: str) -> Dict[str, Any]:
    supabase = get_supabase_client()
    res = supabase.table("student_submissions").update({"status": "published"}).eq("exam_id", exam_id).execute()
    return {"updated_count": len(res.data or []), "status": "published"}


def submit_grade_appeal(submission_id: str, student_reason: str) -> Dict[str, Any]:
    supabase = get_supabase_client()
    payload = {
        "submission_id": submission_id,
        "student_reason": student_reason,
        "status": "pending"
    }
    res = supabase.table("grade_appeals").insert(payload).execute()
    if not res.data:
        raise Exception("Gagal mengirim sanggahan.")
    return res.data[0]


def decide_grade_appeal(appeal_id: str, status: str, teacher_notes: Optional[str] = None) -> Dict[str, Any]:
    supabase = get_supabase_client()
    if status not in ["approved", "rejected"]:
        raise ValueError("Status harus 'approved' atau 'rejected'.")

    payload = {"status": status}
    if teacher_notes:
        payload["teacher_notes"] = teacher_notes

    res = supabase.table("grade_appeals").update(payload).eq("id", appeal_id).execute()
    if not res.data:
        raise Exception(f"Sanggahan dengan ID {appeal_id} tidak ditemukan.")
    return res.data[0]


if __name__ == "__main__":
    sample_title = "Ujian Biologi Dasar - Fotosintesis"
    sample_teacher = "Pak Dosen AI"
    sample_materi = "Materi: Fotosintesis adalah proses tumbuhan mengubah air dan CO2 menjadi glukosa dengan bantuan cahaya matahari di kloroplas."

    print("🚀 Menguji Alur Pembuatan Ujian Otomatis...")
    result = save_exam_to_database(sample_title, sample_teacher, sample_materi)
    
    if result:
        print("\n🎉 FASE 3 BERHASIL 100%!")
        print(f"Detail Ujian: {result}")