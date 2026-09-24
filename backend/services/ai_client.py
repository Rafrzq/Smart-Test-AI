import os
import requests
from dotenv import load_dotenv

load_dotenv()

def get_ai_model_url() -> str:
    url = os.getenv("AI_MODEL_URL") or os.getenv("AGENT_URL") or os.getenv("NGROK_URL") or "http://127.0.0.1:8000"
    if not url.endswith("/generate") and not url.endswith("/api/agent"):
        url = url.rstrip("/") + "/generate"
    return url

def generate_questions(instruction: str, materi_text: str, timeout: int = 60) -> str:
    """
    Panggil model AI fine-tuning via ngrok.
    Return: raw string output dari model (masih perlu di-parse jadi JSON oleh caller).
    """
    ai_url = get_ai_model_url()
    payload = {"prompt": f"{instruction}\n\n{materi_text}"}
    headers = {
        "Content-Type": "application/json",
        "ngrok-skip-browser-warning": "69420"
    }
    try:
        response = requests.post(ai_url, json=payload, headers=headers, timeout=timeout)
        response.raise_for_status()
        res_json = response.json()
        if "response" in res_json:
            return res_json["response"]
        elif "text" in res_json:
            return res_json["text"]
        elif "data" in res_json:
            return str(res_json["data"])
        return response.text
    except requests.exceptions.RequestException as e:
        # Ngrok free tier bisa putus/berubah URL tiap Colab restart — tangani dengan jelas
        raise ConnectionError(f"Gagal menghubungi model AI di {ai_url}: {e}")
