import math
from typing import Dict, Any, List, Optional
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer, util
from agent_engine import query_ai_agent

# Inisialisasi model embedding lokal (ringan & cepat)
similarity_model = SentenceTransformer("all-MiniLM-L6-v2")

try:
    model_embed = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
except Exception:
    model_embed = similarity_model

def grade_essay_draft(jawaban_siswa: str, kunci_jawaban: str) -> dict:
    if not jawaban_siswa or not kunci_jawaban:
        return {"skor_draft": 1, "similarity": 0.0}
    emb1 = model_embed.encode(jawaban_siswa, convert_to_tensor=True)
    emb2 = model_embed.encode(kunci_jawaban, convert_to_tensor=True)
    similarity = util.cos_sim(emb1, emb2).item()

    if similarity >= 0.85:
        skor = 4
    elif similarity >= 0.65:
        skor = 3
    elif similarity >= 0.45:
        skor = 2
    else:
        skor = 1

    return {"skor_draft": skor, "similarity": round(similarity, 3)}



def calculate_exam_duration(questions: List[Dict[str, Any]]) -> int:
    """Mengkalkulasi estimasi durasi ujian (dalam menit) berdasarkan jenis dan panjang soal."""
    total_minutes = 0.0

    for q in questions:
        q_type = q.get("question_type", "pg")
        q_text = q.get("question_text", "")
        word_count = len(q_text.split())

        if q_type == "pg":
            # Baseline PG: 1.5 menit + tambahan berdasarkan jumlah kata
            total_minutes += 1.5 + (word_count / 50.0)
        else:
            # Baseline Esai: 5.0 menit + tambahan untuk analisis
            total_minutes += 5.0 + (word_count / 30.0)

    # Pembulatan ke atas minimum 5 menit
    return max(5, math.ceil(total_minutes))


def compute_semantic_similarity(student_answer: str, rubric_key: str) -> float:
    """Mengkalkulasi nilai kemiripan makna (0.0 - 1.0) menggunakan Cosine Similarity."""
    if not student_answer.strip():
        return 0.0

    # Ubah kalimat menjadi matriks vektor
    embeddings = similarity_model.encode([student_answer, rubric_key])
    
    # Hitung Cosine Similarity antar dua vektor
    similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
    return float(similarity)


def generate_essay_feedback(
    question_text: str, 
    rubric: str, 
    student_answer: str, 
    similarity_score: float
) -> Dict[str, Any]:
    """Memanggil AI Agent (Ngrok / Local) untuk memberikan rekomendasi nilai & evaluasi esai."""
    prompt = (
        f"Soal: {question_text}\n"
        f"Rubrik Penilaian: {rubric}\n"
        f"Jawaban Siswa: {student_answer}\n"
        f"Skor Kesamaan Semantik (NLP): {similarity_score:.2f}\n\n"
        "Berikan rekomendasi nilai esai (0-100) dan alasan evaluasi singkat (1-2 kalimat). "
        "Format respon WAJIB JSON murni: {\"score\": number, \"reason\": \"string\"}"
    )

    try:
        agent_res = query_ai_agent(prompt)
        if agent_res and isinstance(agent_res, dict):
            if "score" in agent_res and "reason" in agent_res:
                return agent_res
            if "data" in agent_res and isinstance(agent_res["data"], dict):
                return agent_res["data"]
            
        # Fallback berbasis Cosine Similarity jika agent tidak memberikan JSON langsung
        estimated_score = round(similarity_score * 100, 2)
        return {
            "score": estimated_score,
            "reason": f"Nilai draf {estimated_score} dihitung berdasarkan kemiripan makna semantik NLP (skor: {similarity_score:.2f})."
        }
    except Exception as err:
        print(f"[WARN] Warning Feedback AI Agent: {err}")
        estimated_score = round(similarity_score * 100, 2)
        return {
            "score": estimated_score,
            "reason": "Nilai draf dihitung berdasarkan kecocokan makna semantik otomatis."
        }


if __name__ == "__main__":
    print("=== Menguji Algoritma Waktu & Auto-Grader Esai via AI Agent ===")

    sample_questions = [
        {"question_type": "pg", "question_text": "Apa fungsi kloroplas pada fotosintesis?"},
        {"question_type": "essai", "question_text": "Jelaskan peran air dalam reaksi fotosintesis!"}
    ]

    duration = calculate_exam_duration(sample_questions)
    print(f"Estimasi Waktu Ujian: {duration} Menit")

    rubric_test = "Air berperan sebagai penyedia elektron dan pemecah molekul menghasilkan oksigen."
    answer_test = "Air berfungsi memecah molekul untuk menghasilkan oksigen dan elektron."

    sim_score = compute_semantic_similarity(answer_test, rubric_test)
    print(f"Skor Similarity NLP: {sim_score:.4f}")

    eval_result = generate_essay_feedback(
        sample_questions[1]["question_text"],
        rubric_test,
        answer_test,
        sim_score
    )
    print(f"Draf Evaluasi AI Agent: {eval_result}")