import requests
import json
import sys

BASE_URL = "http://127.0.0.1:5000"

def test_health():
    print("\n--- 1. Testing Health Check Endpoint ---")
    try:
        res = requests.get(f"{BASE_URL}/api/health", timeout=5)
        print("Status:", res.status_code)
        print("Response:", json.dumps(res.json(), indent=2))
        return res.status_code == 200
    except Exception as e:
        print("[ERROR] Gagal terhubung ke Backend Flask:", e)
        return False

def test_config():
    print("\n--- 2. Testing Config Agent URL Endpoint ---")
    try:
        res = requests.get(f"{BASE_URL}/api/config", timeout=5)
        print("Current Agent URL:", res.json().get("agent_url"))
        return res.status_code == 200
    except Exception as e:
        print("[ERROR] Error Config:", e)
        return False

def test_generate_exam():
    print("\n--- 3. Testing Generate Exam (Menghubungi AI Agent via Ngrok) ---")
    payload = {
        "topic": "Algoritma Pemrograman Python",
        "count": 3
    }
    try:
        res = requests.post(f"{BASE_URL}/api/generate-exam", json=payload, timeout=20)
        print("Status:", res.status_code)
        print("Response:", json.dumps(res.json(), indent=2))
        return res.status_code == 200
    except Exception as e:
        print("[ERROR] Error Generate Exam:", e)
        return False

def test_evaluate_answer():
    print("\n--- 4. Testing Evaluate Essay Answer ---")
    payload = {
        "question_text": "Apa perbedaan List dan Tuple di Python?",
        "student_answer": "List bersifat mutable (bisa diubah), sedangkan Tuple bersifat immutable (tidak bisa diubah setelah dibuat).",
        "rubric": "List mutable, tuple immutable, sintaks siku vs kurung."
    }
    try:
        res = requests.post(f"{BASE_URL}/api/evaluate-answer", json=payload, timeout=30)
        print("Status:", res.status_code)
        print("Response:", json.dumps(res.json(), indent=2))
        return res.status_code == 200
    except Exception as e:
        print("[ERROR] Error Evaluate Answer:", e)
        return False

if __name__ == "__main__":
    print("\n=== MEMULAI PENGUJIAN OTOMATIS BACKEND SMART TEST AI ===")
    
    if not test_health():
        print("\n[ERROR] Backend Flask belum berjalan! Jalankan virtual environment dan python backend/app.py terlebih dahulu.")
        sys.exit(1)
        
    test_config()
    test_generate_exam()
    test_evaluate_answer()
    
    print("\n=== PENGUJIAN SELESAI ===")
