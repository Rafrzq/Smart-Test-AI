# 🤖 Smart Test AI Agent

**Smart Test AI** adalah platform manajemen & evaluasi ujian cerdas yang terintegrasi dengan **AI Agent** berbasis NLP semantik dan konektivitas Ngrok / Localhost API. Platform ini dirancang untuk memudahkan dosen/pengajar dalam membuat soal otomatis serta menilai jawaban essay siswa secara akurat dan transparan.

---

## 🌟 Fitur Utama

- ⚡ **Auto-Generate Soal Ujian**: Membuat paket soal Pilihan Ganda dan Essay secara otomatis menggunakan AI Agent.
- 🎯 **NLP Semantic Essay Grader**: Evaluasi jawaban essay siswa menggunakan algoritma *Cosine Similarity (SentenceTransformers)* dan saran umpan balik dari AI Agent.
- 🔗 **Konektivitas Ngrok & Local Agent**: Terhubung langsung ke AI Agent hasil training kamu via Ngrok URL / HTTP API endpoint.
- 🎮 **Gamified Portal Siswa & Dosen**: Antarmuka interaktif dilengkapi maskot Otti AI, streak, XP, leaderboard, dan animasi perayaan hasil evaluasi.
- 🗄️ **Integrasi Supabase DB**: Penyimpanan bank soal dan riwayat ujian secara terstruktur.

---

## 🏗️ Arsitektur Proyek

Proyek ini dipisah menjadi **Backend (BE)** dan **Frontend (FE)** agar mudah dikembangkan lebih lanjut secara modular.

```
Smart-Test-AI/
├── backend/                  # Flask REST API Server
│   ├── app.py                # Main Flask API Application
│   ├── agent_engine.py       # Client penghubung ke AI Agent (Ngrok/Localhost)
│   ├── grading_service.py    # Algorithmic NLP & Hybrid Essay Evaluator
│   ├── exam_service.py       # Logika bisnis pembuatan ujian & Supabase integration
│   ├── test_db.py            # Koneksi Supabase Database
│   ├── requirements.txt      # Dependencies Python
│   └── .env.example          # Template variabel lingkungan Backend
│
├── frontend/                 # Web Dashboard Frontend
│   ├── index.html            # UI utama Bento Grid (Portal Dosen & Siswa)
│   ├── style.css             # Desain CSS modern & gamifikasi maskot Otti
│   ├── script.js             # Interaksi JS & HTTP Client Backend
│   ├── smart-test-ui/        # Optional Vite/React app template
│   └── package.json          # Node dependencies
│
├── .gitignore                # Aturan pembatasan file Git
└── README.md                 # Dokumentasi utama proyek
```

---

## 🌿 Branching Strategy

Untuk memfasilitasi pengembangan mandiri pada Backend & Frontend, repositori ini mengadopsi struktur branch berikut:

- `main` : Kode produksi utama (Modul gabungan Backend + Frontend).
- `backend` : Branch khusus untuk pengembangan fitur server Python Flask & AI Engine.
- `frontend` : Branch khusus untuk pengembangan UI/UX HTML, CSS, JS, dan React UI.

---

## 🚀 Panduan Memulai (Setup Guide)

### 1. Clone Repositori

```bash
git clone https://github.com/Rafrzq/Smart-Test-AI.git
cd Smart-Test-AI
```

### 2. Setup Backend (Python Flask)

```bash
# Masuk ke direktori backend (atau jalankan di root)
cd backend

# Buat virtual environment
python -m venv venv

# Aktifkan virtual environment
# Windows:
.\venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependensi
pip install -r requirements.txt

# Salin .env.example menjadi .env
cp .env.example .env
```

Isi file `.env` dengan konfigurasi milikmu:
```env
SUPABASE_URL=https://your-supabase-url.supabase.co
SUPABASE_KEY=your-supabase-anon-key

# URL AI Agent latihan kamu (Ngrok atau Localhost)
AGENT_URL=http://127.0.0.1:8000
NGROK_URL=https://your-ngrok-url.ngrok-free.app
```

Jalankan Flask API server:
```bash
python app.py
```
*Server Backend akan berjalan di `http://localhost:5000`.*

---

### 3. Setup Frontend

1. Buka file `frontend/index.html` langsung di browser favoritmu, atau gunakan extension **Live Server** di VS Code.
2. Pastikan backend Flask (`http://localhost:5000`) sudah berjalan agar fitur **Generate Ujian** dan **Evaluasi Jawaban** terhubung secara live.

---

## 🔌 Cara Menghubungkan AI Agent (Ngrok)

1. Jalankan server AI Agent latihan kamu di local (misal port 8000).
2. Ekspos port agent menggunakan Ngrok:
   ```bash
   ngrok http 8000
   ```
3. Salin URL publik Ngrok (contoh: `https://xxxx-xx-xxx.ngrok-free.app`).
4. Tempelkan URL tersebut pada file `.env` di variabel `NGROK_URL` atau `AGENT_URL`, lalu restart backend Flask.

---

## 📝 Lisensi & Penulis

Dikembangkan oleh **Raffi Sya Dwi Razzaq** ([@Rafrzq](https://github.com/Rafrzq)).  
Dibuat untuk keperluan tugas & proyek AI Agent Smart Test. 🚀
