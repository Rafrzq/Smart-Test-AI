const { test, expect } = require('@playwright/test');

test.describe('Smart Test AI - E2E Portal & Otti Mascot Tests', () => {

  test.beforeEach(async ({ page }) => {
    // Buka aplikasi web lokal
    await page.goto('/index.html');
  });

  test('1. Verifikasi Elemen Utama & Status Awal Otti', async ({ page }) => {
    // Cek Judul Portal
    await expect(page.locator('#hero-title')).toContainText('Dr. Budi');
    
    // Cek Status Awal Mascot Otti
    const ottiStatus = page.locator('#otti-status-text');
    await expect(ottiStatus).toContainText('Ready to Help');
  });

  test('2. Uji Pergantian Portal Dosen ke Portal Siswa', async ({ page }) => {
    // Klik Tab Portal Siswa
    await page.click('#btn-portal-siswa');

    // Pastikan Tampilan Siswa Aktif
    await expect(page.locator('#view-siswa')).toBeVisible();
    await expect(page.locator('#hero-title')).toContainText('Semangat Belajar');

    // Klik Kembali ke Portal Dosen
    await page.click('#btn-portal-dosen');
    await expect(page.locator('#view-dosen')).toBeVisible();
  });

  test('3. Uji Pengubah Expression Mascot Otti (State Switcher)', async ({ page }) => {
    // Klik tombol state "Buat Soal"
    await page.click('button:has-text("Buat Soal")');
    await expect(page.locator('#otti-status-text')).toContainText('Membuat Soal');

    // Klik tombol state "Nilai 100"
    await page.click('button:has-text("Nilai 100")');
    await expect(page.locator('#otti-status-text')).toContainText('Nilai 100');
  });

  test('4. Simulasi Submit Ujian Siswa & Evaluasi Otti AI Grader', async ({ page }) => {
    // Pindah ke Portal Siswa
    await page.click('#btn-portal-siswa');

    // Isi Textarea Jawaban Siswa
    await page.fill('#student-answer-input', 'Array menyimpan data secara kontigu sedangkan Linked List menggunakan node berantai.');

    // Klik Kirim Jawaban (Simulasi Nilai 100)
    await page.click('button:has-text("Kirim Jawaban Bagus")');

    // Tunggu evaluasi selesai (Feedback Box Tampak)
    const feedbackBox = page.locator('#otti-feedback-box');
    await expect(feedbackBox).toBeVisible({ timeout: 5000 });
    await expect(page.locator('#result-score-val')).toContainText('100');
  });

});
