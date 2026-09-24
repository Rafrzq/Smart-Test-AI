import os
import json
import requests
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

AGENT_URL = os.getenv("AGENT_URL") or os.getenv("NGROK_URL") or "http://127.0.0.1:8000"

def get_agent_url() -> str:
    """Mendapatkan URL AI Agent (Ngrok / Localhost)."""
    return os.getenv("AGENT_URL") or os.getenv("NGROK_URL") or "http://127.0.0.1:8000"

def set_agent_url(url: str):
    """Mengatur URL AI Agent secara dinamis."""
    global AGENT_URL
    AGENT_URL = url.rstrip('/')
    os.environ["AGENT_URL"] = AGENT_URL

def sanitize_and_parse_json(raw_text: str) -> Optional[Dict[str, Any]]:
    """Membersihkan dan memvalidasi teks JSON dari respons AI Agent."""
    try:
        clean_text = raw_text.strip()
        if clean_text.startswith("```json"):
            clean_text = clean_text[7:]
        if clean_text.startswith("```"):
            clean_text = clean_text[3:]
        if clean_text.endswith("```"):
            clean_text = clean_text[:-3]
        clean_text = clean_text.strip()
        
        parsed_data = json.loads(clean_text)
        return parsed_data
    except Exception as parse_err:
        print(f"[ERROR] Parsing JSON AI Agent: {parse_err}")
        return None

def query_ai_agent(prompt: str, payload: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
    """
    Mengirimkan prompt / request ke AI Agent via Ngrok / HTTP Endpoint.
    Mendukung format request umum uagents / Custom Flask / FastApi agent.
    """
    url = get_agent_url()
    
    # Deteksi endpoint (ngrok URL atau localhost)
    endpoints = [
        f"{url}/api/agent",
        f"{url}/generate",
        f"{url}/submit",
        f"{url}/chat",
        url
    ]
    
    headers = {
        "Content-Type": "application/json",
        "ngrok-skip-browser-warning": "69420"  # Bypass Ngrok warning page jika pakai Ngrok Free
    }
    
    req_body = payload if payload else {"prompt": prompt, "message": prompt}
    
    for ep in endpoints:
        try:
            print(f"--> Menghubungi AI Agent di: {ep}...")
            response = requests.post(ep, json=req_body, headers=headers, timeout=15)
            if response.status_code == 200:
                try:
                    res_data = response.json()
                    print(f"[OK] Respons dari AI Agent diterima!")
                    return res_data
                except Exception as json_err:
                    print(f"[WARN] Response status 200 tapi bukan JSON (Ngrok warning page): {json_err}")
                    continue
            elif response.status_code == 404:
                continue
        except Exception as e:
            print(f"[WARN] Mencoba endpoint {ep} gagal: {e}")
            continue

    print(f"[ERROR] Gagal menghubungi AI Agent di {url}")
    return None

def generate_exam_questions(materi_text: str, count: int = 5) -> Optional[Dict[str, Any]]:
    """Fungsi utama untuk meminta AI Agent hasil latihan/Ngrok membuat soal."""
    system_instruction = (
        f"Buatkan {count} soal ujian untuk materi: {materi_text}.\n"
        "Format JSON murni wajib:\n"
        "{\n"
        '  "pg": [\n'
        '    {"soal": "string", "opsi": ["A. ...", "B. ...", "C. ...", "D. ..."], "jawaban": "A. ...", "level": "C4"}\n'
        "  ],\n"
        '  "essai": [\n'
        '    {"soal": "string", "rubrik": "string"}\n'
        "  ]\n"
        "}"
    )
    
    payload = {
        "materi": materi_text,
        "count": count,
        "prompt": system_instruction
    }
    
    res = query_ai_agent(system_instruction, payload)
    
    if res and isinstance(res, dict):
        if "data" in res and isinstance(res["data"], dict):
            return res["data"]
        if "pg" in res and "essai" in res:
            return res
        if "text" in res or "response" in res:
            text = res.get("text") or res.get("response")
            return sanitize_and_parse_json(text)
            
    # Return mock fallback jika Agent belum aktif/ngrok belum tersambung
    return {
        "pg": [
            {
                "soal": f"Apa konsep utama dari {materi_text}?",
                "opsi": ["A. Statis", "B. Dinamis & Terstruktur", "C. Asinkron", "D. Paralel"],
                "jawaban": "B. Dinamis & Terstruktur",
                "level": "C4"
            }
        ],
        "essai": [
            {
                "soal": f"Jelaskan implementasi dan analisis kompleksitas dari {materi_text}!",
                "rubrik": "Jawaban memuat penjelasan konsep, efisiensi memori, dan contoh penerapan."
            }
        ]
    }
