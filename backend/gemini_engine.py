import os
import sys
import json
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Standardize output encoding for Windows terminal compatibility
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Load environment variables
load_dotenv()

# Configuration Constants
GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
MODEL_NAME: str = "gemini-2.5-flash"


def get_gemini_client() -> genai.Client:
    """Fungsi untuk menginisialisasi Client Google GenAI."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY belum diatur di file .env")
    return genai.Client(api_key=api_key)


def construct_system_instruction() -> str:
    """Fungsi untuk mengembalikan instruksi sistem (System Prompt) pembatas format JSON."""
    return (
        "Kamu adalah AI Agent pembuat soal ujian profesional. "
        "Tugas utama kamu adalah mengekstraksi materi pelajaran yang diberikan user menjadi paket soal. "
        "Jawaban WAJIB dalam format JSON murni tanpa ada pembuka/penutup teks markdown. "
        "Struktur JSON harus persis seperti ini:\n"
        "{\n"
        '  "pg": [\n'
        '    {"soal": "string", "opsi": ["A. ...", "B. ...", "C. ...", "D. ..."], "jawaban": "A", "level": "C4"}\n'
        "  ],\n"
        '  "essai": [\n'
        '    {"soal": "string", "rubrik": "string"}\n'
        "  ]\n"
        "}"
    )


def sanitize_and_parse_json(raw_text: str) -> Optional[Dict[str, Any]]:
    """Fungsi algoritma sanitasi lokal untuk membersihkan dan memvalidasi teks JSON dari API."""
    try:
        clean_text = raw_text.strip()
        
        # Membersihkan pembungkus markdown ```json jika ada
        if clean_text.startswith("```json"):
            clean_text = clean_text[7:]
        if clean_text.startswith("```"):
            clean_text = clean_text[3:]
        if clean_text.endswith("```"):
            clean_text = clean_text[:-3]
            
        clean_text = clean_text.strip()
        
        # Validasi parsing teks ke objek Python Dictionary
        parsed_data = json.loads(clean_text)
        
        # Algoritma sanitasi struktur data wajib
        if "pg" not in parsed_data or "essai" not in parsed_data:
            raise KeyError("Format JSON hasil API tidak memiliki kunci utama 'pg' atau 'essai'")
            
        return parsed_data

    except (json.JSONDecodeError, KeyError) as parse_err:
        print(f"❌ ERROR Sanitasi JSON: Output API cacat atau tidak sesuai format | Detail: {parse_err}")
        return None


def generate_exam_questions(materi_text: str) -> Optional[Dict[str, Any]]:
    """Fungsi utama untuk memanggil Gemini API dan memproses ekstraksi soal."""
    try:
        client = get_gemini_client()
        system_prompt = construct_system_instruction()
        
        # Konfigurasi parameter request Gemini
        config = types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.2, # Temperature rendah agar output konsisten dan presisi
            response_mime_type="application/json" # Memaksa Gemini merespon hanya dalam format JSON
        )
        
        print("🔄 Mengirim materi ke Gemini API Engine...")
        
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=f"Materi: {materi_text}",
            config=config
        )
        
        # Eksekusi sanitasi lokal terhadap respon Gemini
        validated_json = sanitize_and_parse_json(response.text)
        return validated_json

    except ValueError as config_err:
        print(f"❌ ERROR Konfigurasi: {config_err}")
    except Exception as api_err:
        print(f"❌ ERROR Panggilan Gemini API: {api_err}")
    return None


if __name__ == "__main__":
    # Test pembuatan soal dengan materi sampel
    sample_materi = "Materi: Fotosintesis terjadi di kloroplas menggunakan cahaya matahari untuk mengubah CO2 dan air menjadi glukosa."
    result = generate_exam_questions(sample_materi)
    
    if result:
        print("\n✅ SUCCESS: Gemini API & Algoritma Sanitasi Berhasil!")
        print("--- HASIL PARSING DATA DARI AGENT ---")
        print(json.dumps(result, indent=2, ensure_ascii=False))