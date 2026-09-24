# Smart-Test AI — Instruksi Perbaikan (Patch Mode)
> Dokumen ini untuk AI coding agent (Antigravity). **Mode kerja: PERBAIKAN/PATCH, BUKAN rebuild total.** Website sudah setengah jadi, model AI sudah selesai di-fine-tune dan sudah aktif lewat ngrok. Jangan tulis ulang file/komponen yang sudah berjalan dengan benar — hanya tambahkan bagian yang belum ada dan perbaiki bagian yang belum sesuai rencana di bawah.

---

## 0. Langkah wajib SEBELUM mengubah kode apapun

1. Scan seluruh struktur folder project saat ini (`smart test BE and FE`) — list semua file/route/komponen yang sudah ada.
2. Cocokkan dengan rencana arsitektur di `SMART_TEST_AI_FLOW.md` (kalau file itu ada di project, baca dulu isinya).
3. Buat daftar: **(a)** bagian yang sudah sesuai rencana → **JANGAN disentuh**, **(b)** bagian yang belum ada → buat baru mengikuti spesifikasi di bawah, **(c)** bagian yang ada tapi menyimpang dari rencana → perbaiki seminimal mungkin, jangan hapus logika lain yang tidak terkait.
4. Kalau ada keraguan apakah sesuatu boleh diubah atau tidak, **jangan tebak — tanya dulu ke user sebelum eksekusi.**

---

## 1. Status Saat Ini (konteks, bukan tugas)
- Model AI: Llama-3-8B fine-tuned sudah selesai training pakai dataset `dataset_soal_v2.jsonl` (+ data lama).
- Model sudah di-deploy sementara via **Colab + FastAPI + ngrok** (endpoint `POST /generate`).
- Supabase: akun & project sudah dibuat, **tapi tabel database BELUM ada** — ini yang perlu dieksekusi di langkah 2.

---

## 2. Database Supabase — WAJIB dijalankan (belum ada tabel sama sekali)

Jalankan seluruh isi file **`supabase_schema.sql`** (satu file terpisah, sudah disediakan) di **SQL Editor Supabase** dalam satu kali run. Itu sudah final dan sesuai rencana arsitektur — 6 tabel: `teachers`, `materials`, `exams`, `questions`, `student_submissions`, `grade_appeals`.

Setelah tabel jadi, ambil kembali `Project URL` dan `anon/service_role key` dari Supabase API Settings, pastikan sudah cocok dengan yang ada di `.env` project (kalau beda dari sebelumnya, update `.env`).

---

## 3. Koneksi Backend ↔ Model AI (ngrok)

Karena kamu sudah punya URL ngrok aktif, tambahkan (jangan hardcode di file kode):

```
# .env — tambahkan baris ini
AI_MODEL_URL=<paste_url_ngrok_kamu_di_sini>/generate
```

Buat/perbaiki satu fungsi wrapper terpusat di backend (misal `services/ai_client.py`) supaya semua endpoint yang butuh manggil model AI lewat 1 fungsi ini saja — jangan panggil `requests.post()` langsung tersebar di banyak file:

```python
import os
import requests

AI_MODEL_URL = os.getenv("AI_MODEL_URL")

def generate_questions(instruction: str, materi_text: str, timeout: int = 60) -> str:
    """
    Panggil model AI fine-tuning via ngrok.
    Return: raw string output dari model (masih perlu di-parse jadi JSON oleh caller).
    """
    payload = {"prompt": f"{instruction}\n\n{materi_text}"}
    try:
        response = requests.post(AI_MODEL_URL, json=payload, timeout=timeout)
        response.raise_for_status()
        return response.json()["response"]
    except requests.exceptions.RequestException as e:
        # Ngrok free tier bisa putus/berubah URL tiap Colab restart — tangani dengan jelas
        raise ConnectionError(f"Gagal menghubungi model AI di {AI_MODEL_URL}: {e}")
```

**Catatan penting:** URL ngrok gratis **berubah setiap kali Colab session di-restart**. Jangan taruh URL ini di kode manapun selain `.env`, supaya kamu tinggal update 1 baris tiap kali Colab restart, bukan cari-cari di banyak file.

**Catatan keamanan:** di notebook Colab kamu ada `NGROK_TOKEN` yang ditulis langsung di kode (hardcoded). Sebaiknya pindahkan juga ke Colab Secrets atau input manual tiap run, jangan disimpan permanen di notebook yang mungkin ke-share/ke-push ke GitHub.

---

## 4. Endpoint Backend — Tambahkan yang Belum Ada

Cek dulu satu per satu, mana yang sudah ada di project. Untuk yang **belum ada**, tambahkan endpoint berikut (FastAPI):

| Endpoint | Method | Fungsi |
|---|---|---|
| `/materi/upload` | POST | Terima file PDF/DOCX + `jumlah_pg`, `jumlah_essai`, `level_distribution` dari form pengajar → extract teks (pdfplumber) → panggil `generate_questions()` → simpan hasil ke tabel `materials` (status `processing` → `generated`) dan `questions` (status `draft`) |
| `/bank-soal/{materi_id}` | GET | Ambil semua soal draft dari 1 materi untuk direview pengajar |
| `/bank-soal/{soal_id}` | PUT | Pengajar edit isi soal sebelum di-approve |
| `/bank-soal/{soal_id}/approve` | PATCH | Ubah status soal dari `draft` → `approved` |
| `/ujian/buat` | POST | Terima `material_id`, `questions_shown_per_student`, `duration_minutes` dari pengajar → generate `exam_code` 6 digit unik → insert ke `exams` |
| `/ujian/{kode}/mulai` | POST | Siswa kirim `nama`, `nis`, `kode` → validasi kode exam ada & masih aktif → ambil N soal approved secara acak (`ORDER BY random() LIMIT n`) → acak urutan opsi A/B/C/D per soal → return soal **tanpa** `correct_answer` |
| `/ujian/{kode}/submit` | POST | Terima jawaban siswa → insert ke `student_submissions` → jalankan auto-grading PG (exact match) → jalankan draft-grading esai (similarity, lihat bagian 5) → simpan skor dengan status `pending_review` |
| `/ujian/{id}/hasil` | GET | Pengajar lihat rekap nilai semua siswa untuk 1 ujian |
| `/ujian/{id}/rilis` | PATCH | Ubah status semua submission dari `pending_review` → `published` |
| `/sanggahan` | POST | Siswa ajukan sanggahan skor esai → insert ke `grade_appeals` |
| `/sanggahan/{id}/keputusan` | PATCH | Pengajar approve/reject sanggahan |

Kalau sebagian endpoint di atas **sudah ada** tapi belum lengkap (misal belum ada shuffle, belum connect ke DB beneran), perbaiki isinya saja — jangan ganti nama route atau struktur folder yang sudah dipakai frontend.

---

## 5. Auto-Grading Esai (ML similarity) — tambahkan kalau belum ada

```python
from sentence_transformers import SentenceTransformer, util

model_embed = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

def grade_essay_draft(jawaban_siswa: str, kunci_jawaban: str) -> dict:
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
```

Tambahkan `sentence-transformers` ke `requirements.txt` / install via `pip install sentence-transformers --break-system-packages` di venv project. Model ini jalan lokal (CPU laptop), tidak butuh koneksi ke Colab/ngrok.

---

## 6. Frontend — Cek & Lengkapi (bukan rombak)

- Portal Pengajar (`/login`, `/dashboard`, `/materi/upload`, `/bank-soal`, `/ujian/buat`, `/ujian/:id/hasil`, `/ujian/:id/sanggahan`) — kalau route sudah ada tapi belum connect ke endpoint di atas, tinggal sambungkan `fetch`/`requests` ke URL backend, **jangan desain ulang komponennya**.
- Portal Siswa (`/join`, `/ujian/:kode/kerjakan`, `/ujian/:kode/selesai`, `/ujian/:kode/hasil`) — sama, cek dulu yang sudah ada, sambungkan yang belum.
- Kalau ada halaman yang benar-benar belum ada sama sekali, baru buat baru sesuai spesifikasi routing di `SMART_TEST_AI_FLOW.md`.

---

## 7. Checklist Testing Setelah Patch

- [ ] Jalankan `supabase_schema.sql`, pastikan 6 tabel muncul di Supabase Table Editor
- [ ] Test `.env` `AI_MODEL_URL` nyambung — hit endpoint ngrok langsung pakai Postman/curl dulu sebelum lewat backend
- [ ] Test `/materi/upload` dengan 1 PDF kecil, cek soal masuk ke tabel `questions` dengan status `draft`
- [ ] Test `/ujian/buat` menghasilkan `exam_code` unik
- [ ] Test 2 browser berbeda join `/ujian/{kode}/mulai` dengan kode sama → pastikan urutan soal & opsi A/B/C/D beda antar keduanya
- [ ] Test submit jawaban → skor PG langsung muncul, skor esai berstatus draft
- [ ] Test alur sanggahan siswa → keputusan pengajar
