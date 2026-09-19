import random
import string
from typing import Dict, Any, Optional, List
from agent_engine import generate_exam_questions
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
    # 1. Panggil Gemini Engine untuk meng-generate soal
    ai_response = generate_exam_questions(materi_text)
    if not ai_response:
        print("❌ ERROR: Gagal mendapatkan respon dari AI Agent.")
        return None

    try:
        supabase = get_supabase_client()
        exam_code = generate_unique_exam_code()

        # 2. Simpan header data ujian ke tabel 'exams'
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

        # 3. Format dan siapkan batch data soal untuk tabel 'questions'
        questions_to_insert: List[Dict[str, Any]] = []

        # Process Pilihan Ganda
        for pg_item in ai_response.get("pg", []):
            questions_to_insert.append({
                "exam_id": exam_id,
                "question_type": "pg",
                "question_text": pg_item.get("soal", ""),
                "options": pg_item.get("opsi", []),
                "correct_answer": pg_item.get("jawaban", ""),
                "difficulty_level": pg_item.get("level", "C4")
            })

        # Process Esai
        for essai_item in ai_response.get("essai", []):
            questions_to_insert.append({
                "exam_id": exam_id,
                "question_type": "essai",
                "question_text": essai_item.get("soal", ""),
                "correct_answer": "Sesuai Rubrik",
                "rubric_essay": essai_item.get("rubrik", ""),
                "difficulty_level": "C4"
            })

        # 4. Insert seluruh bank soal sekaligus (Batch Insert)
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


if __name__ == "__main__":
    # Test jalankan pembuatan ujian dari backend
    sample_title = "Ujian Biologi Dasar - Fotosintesis"
    sample_teacher = "Pak Dosen AI"
    sample_materi = "Materi: Fotosintesis adalah proses tumbuhan mengubah air dan CO2 menjadi glukosa dengan bantuan cahaya matahari di kloroplas."

    print("🚀 Menguji Alur Pembuatan Ujian Otomatis...")
    result = save_exam_to_database(sample_title, sample_teacher, sample_materi)
    
    if result:
        print("\n🎉 FASE 3 BERHASIL 100%!")
        print(f"Detail Ujian: {result}")