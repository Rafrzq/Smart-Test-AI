import os
from typing import Optional
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv()

# Configuration Constants
SUPABASE_URL: Optional[str] = os.getenv("SUPABASE_URL")
SUPABASE_KEY: Optional[str] = os.getenv("SUPABASE_KEY")


def get_supabase_client() -> Client:
    """Fungsi untuk membuat dan mengembalikan instance Supabase Client."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("SUPABASE_URL atau SUPABASE_KEY belum diatur di file .env")
    return create_client(SUPABASE_URL, SUPABASE_KEY)


def test_database_connection() -> None:
    """Fungsi untuk menguji koneksi read ke tabel 'exams' di Supabase."""
    try:
        supabase_client = get_supabase_client()
        
        # Eksekusi query baca ringan
        response = supabase_client.table("exams").select("id").limit(1).execute()
        
        print("✅ SUCCESS: Koneksi ke Supabase Berhasil!")
        print(f"Data Respon: {response.data}")
        
    except ValueError as val_err:
        print(f"❌ ERROR Konfigurasi: {val_err}")
    except Exception as err:
        print(f"❌ ERROR Koneksi Database: {err}")


if __name__ == "__main__":
    test_database_connection()