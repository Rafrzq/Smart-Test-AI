/* ==========================================================================
   SMART TEST AI - JAVASCRIPT INTERACTION & OTTI MASCOT CONTROLLER
   ========================================================================== */

// 1. OTTI MASCOT SVG VARIANTS & SPEECH DICTIONARY
const ottiVariants = {
  classic: {
    badge: "Otti: Ready to Help!",
    speech: "Selamat datang! Pilih aksi di bawah untuk mulai buat soal ujian!",
    svg: `
      <svg viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
        <!-- Body -->
        <ellipse cx="50" cy="55" rx="32" ry="34" fill="#a06645"/>
        <ellipse cx="50" cy="58" rx="22" ry="24" fill="#f5d5b6"/>
        <!-- Ears -->
        <circle cx="24" cy="28" r="8" fill="#a06645"/>
        <circle cx="24" cy="28" r="4" fill="#7a462b"/>
        <circle cx="76" cy="28" r="8" fill="#a06645"/>
        <circle cx="76" cy="28" r="4" fill="#7a462b"/>
        <!-- Eyes & Cheeks -->
        <circle cx="38" cy="42" r="4" fill="#2d1a10"/>
        <circle cx="62" cy="42" r="4" fill="#2d1a10"/>
        <circle cx="39" cy="40" r="1.5" fill="#ffffff"/>
        <circle cx="63" cy="40" r="1.5" fill="#ffffff"/>
        <circle cx="32" cy="47" r="5" fill="#f87171" opacity="0.5"/>
        <circle cx="68" cy="47" r="5" fill="#f87171" opacity="0.5"/>
        <!-- Nose & Mouth -->
        <ellipse cx="50" cy="46" rx="4" ry="3" fill="#3a1e05"/>
        <path d="M46 50 Q50 54 54 50" stroke="#3a1e05" stroke-width="2" stroke-linecap="round"/>
        <!-- Paws waving -->
        <ellipse cx="22" cy="54" rx="6" ry="10" fill="#a06645" transform="rotate(30 22 54)"/>
        <ellipse cx="78" cy="48" rx="6" ry="10" fill="#a06645" transform="rotate(-40 78 48)"/>
        <!-- Backpack -->
        <rect x="16" y="58" width="10" height="20" rx="4" fill="#1cb0f6"/>
      </svg>
    `
  },
  buat_soal: {
    badge: "Otti: Membuat Soal Ujian AI...",
    speech: "Sedang meracik soal essay bertingkat sesuai indikator pembelajaran...",
    svg: `
      <svg viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
        <ellipse cx="50" cy="55" rx="32" ry="34" fill="#a06645"/>
        <ellipse cx="50" cy="58" rx="22" ry="24" fill="#f5d5b6"/>
        <circle cx="24" cy="28" r="8" fill="#a06645"/>
        <circle cx="76" cy="28" r="8" fill="#a06645"/>
        <!-- Glasses for Professor Otti -->
        <circle cx="38" cy="42" r="9" stroke="#3a1e05" stroke-width="2.5" fill="none"/>
        <circle cx="62" cy="42" r="9" stroke="#3a1e05" stroke-width="2.5" fill="none"/>
        <line x1="47" y1="42" x2="53" y2="42" stroke="#3a1e05" stroke-width="2.5"/>
        <circle cx="38" cy="42" r="3" fill="#2d1a10"/>
        <circle cx="62" cy="42" r="3" fill="#2d1a10"/>
        <ellipse cx="50" cy="48" rx="4" ry="3" fill="#3a1e05"/>
        <path d="M47 52 Q50 55 53 52" stroke="#3a1e05" stroke-width="2"/>
        <!-- Laptop -->
        <rect x="30" y="65" width="40" height="22" rx="3" fill="#cbd5e1" stroke="#64748b" stroke-width="2"/>
        <path d="M24 87 L76 87 L72 91 L28 91 Z" fill="#94a3b8"/>
        <!-- Sparkles AI -->
        <path d="M82 20 L84 25 L89 27 L84 29 L82 34 L80 29 L75 27 L80 25 Z" fill="#ffc800"/>
      </svg>
    `
  },
  loading: {
    badge: "Otti: Berpikir & Memproses...",
    speech: "Tunggu sebentar ya... Otti sedang mengolah data ujian dengan AI...",
    svg: `
      <svg viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
        <!-- Otti Lying Down Sleeping/Thinking -->
        <ellipse cx="50" cy="65" rx="38" ry="22" fill="#a06645"/>
        <ellipse cx="50" cy="68" rx="26" ry="14" fill="#f5d5b6"/>
        <circle cx="20" cy="55" r="7" fill="#a06645"/>
        <circle cx="80" cy="55" r="7" fill="#a06645"/>
        <!-- Closed Sleeping Eyes -->
        <path d="M34 60 Q38 64 42 60" stroke="#2d1a10" stroke-width="2.5" stroke-linecap="round"/>
        <path d="M58 60 Q62 64 66 60" stroke="#2d1a10" stroke-width="2.5" stroke-linecap="round"/>
        <ellipse cx="50" cy="63" rx="3" ry="2" fill="#3a1e05"/>
        <!-- Zzz animation bubbles -->
        <text x="70" y="35" font-family="Fredoka" font-size="14" font-weight="bold" fill="#ce82ff">z</text>
        <text x="80" y="24" font-family="Fredoka" font-size="18" font-weight="bold" fill="#1cb0f6">Z</text>
        <text x="60" y="42" font-family="Fredoka" font-size="10" font-weight="bold" fill="#ff9600">z</text>
      </svg>
    `
  },
  menilai: {
    badge: "Otti: Menilai Jawaban...",
    speech: "Sedang memeriksa lembar jawaban essay siswa terhadap kunci jawaban...",
    svg: `
      <svg viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
        <ellipse cx="50" cy="55" rx="32" ry="34" fill="#a06645"/>
        <ellipse cx="50" cy="58" rx="22" ry="24" fill="#f5d5b6"/>
        <circle cx="24" cy="28" r="8" fill="#a06645"/>
        <circle cx="76" cy="28" r="8" fill="#a06645"/>
        <!-- Concentrated Eyes -->
        <circle cx="38" cy="42" r="3" fill="#2d1a10"/>
        <circle cx="62" cy="42" r="3" fill="#2d1a10"/>
        <ellipse cx="50" cy="46" rx="4" ry="2" fill="#3a1e05"/>
        <line x1="46" y1="52" x2="54" y2="52" stroke="#3a1e05" stroke-width="2"/>
        <!-- Magnifying Glass -->
        <circle cx="65" cy="62" r="12" stroke="#ff9600" stroke-width="3" fill="none"/>
        <line x1="74" y1="71" x2="86" y2="83" stroke="#ff9600" stroke-width="4" stroke-linecap="round"/>
        <!-- Paper document -->
        <rect x="22" y="58" width="22" height="28" rx="2" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.5"/>
        <line x1="26" y1="64" x2="38" y2="64" stroke="#58cc02" stroke-width="2"/>
        <line x1="26" y1="70" x2="40" y2="70" stroke="#cbd5e1" stroke-width="1.5"/>
        <line x1="26" y1="76" x2="35" y2="76" stroke="#cbd5e1" stroke-width="1.5"/>
      </svg>
    `
  },
  nilai_bagus: {
    badge: "Otti: Sempurna! (Nilai 100)",
    speech: "Luar biasa! Kamu dapat nilai 100! Teruskan semangat belajarmu!",
    svg: `
      <svg viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
        <ellipse cx="50" cy="55" rx="32" ry="34" fill="#a06645"/>
        <ellipse cx="50" cy="58" rx="22" ry="24" fill="#f5d5b6"/>
        <circle cx="24" cy="28" r="8" fill="#a06645"/>
        <circle cx="76" cy="28" r="8" fill="#a06645"/>
        <!-- Cheerful Winking Eyes -->
        <path d="M32 42 Q38 36 44 42" stroke="#2d1a10" stroke-width="3" stroke-linecap="round"/>
        <circle cx="62" cy="40" r="4" fill="#2d1a10"/>
        <circle cx="63" cy="38" r="1.5" fill="#ffffff"/>
        <circle cx="32" cy="46" r="5" fill="#f87171" opacity="0.6"/>
        <circle cx="68" cy="46" r="5" fill="#f87171" opacity="0.6"/>
        <!-- Big Happy Mouth -->
        <path d="M42 48 Q50 60 58 48 Z" fill="#ff4b4b"/>
        <!-- Graduation Cap -->
        <path d="M25 24 L50 14 L75 24 L50 32 Z" fill="#1e293b"/>
        <rect x="36" y="24" width="28" height="8" fill="#334155"/>
        <path d="M72 24 L72 34 L70 36" stroke="#ffc800" stroke-width="2"/>
        <!-- Holding 100 Paper -->
        <rect x="62" y="55" width="26" height="32" rx="3" fill="#ffffff" stroke="#58cc02" stroke-width="2" transform="rotate(15 62 55)"/>
        <text x="66" y="78" font-family="Fredoka" font-size="14" font-weight="bold" fill="#ff4b4b" transform="rotate(15 62 55)">100</text>
      </svg>
    `
  },
  nilai_kurang: {
    badge: "Otti: Tetap Semangat! (Nilai 60)",
    speech: "Tidak apa-apa! Jangan menyerah, yuk pelajari kembali bagian yang belum paham!",
    svg: `
      <svg viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
        <ellipse cx="50" cy="55" rx="32" ry="34" fill="#a06645"/>
        <ellipse cx="50" cy="58" rx="22" ry="24" fill="#f5d5b6"/>
        <circle cx="24" cy="28" r="8" fill="#a06645"/>
        <circle cx="76" cy="28" r="8" fill="#a06645"/>
        <!-- Comforting / Encouraging Eyes -->
        <circle cx="38" cy="42" r="3.5" fill="#2d1a10"/>
        <circle cx="62" cy="42" r="3.5" fill="#2d1a10"/>
        <!-- Sad/Comforting Mouth -->
        <path d="M45 52 Q50 49 55 52" stroke="#3a1e05" stroke-width="2.5" stroke-linecap="round"/>
        <!-- Sweat droplet -->
        <path d="M28 36 C28 36 25 40 27 42 C29 44 31 42 31 40 C31 38 28 36 28 36 Z" fill="#38bdf8"/>
        <!-- Holding 60 Paper -->
        <rect x="60" y="58" width="24" height="30" rx="3" fill="#ffffff" stroke="#ff9600" stroke-width="2"/>
        <text x="65" y="78" font-family="Fredoka" font-size="13" font-weight="bold" fill="#ff9600">60</text>
        <!-- Heart of support -->
        <path d="M18 65 C18 62 22 60 24 63 C26 60 30 62 30 65 C30 69 24 73 24 73 C24 73 18 69 18 65 Z" fill="#ff4b4b"/>
      </svg>
    `
  }
};

// 2. SWITCH OTTI STATE FUNCTION
function setOttiState(stateName) {
  const data = ottiVariants[stateName] || ottiVariants.classic;
  
  // Update status text
  const statusEl = document.getElementById('otti-status-text');
  if (statusEl) statusEl.textContent = data.badge;

  // Update speech bubble
  const speechEl = document.getElementById('otti-speech');
  if (speechEl) speechEl.textContent = `"${data.speech}"`;

  // Render SVG Mascot
  const mascotDisplay = document.getElementById('otti-mascot-display');
  if (mascotDisplay) {
    mascotDisplay.className = `otti-mascot-state state-${stateName}`;
    mascotDisplay.innerHTML = data.svg;
  }

  // Active state button update
  document.querySelectorAll('.otti-state-btn').forEach(btn => {
    btn.classList.remove('active');
    if (btn.getAttribute('onclick')?.includes(stateName)) {
      btn.classList.add('active');
    }
  });
}

// 3. PORTAL SWITCHER (DOSEN <-> SISWA)
function switchPortal(portalType) {
  const btnDosen = document.getElementById('btn-portal-dosen');
  const btnSiswa = document.getElementById('btn-portal-siswa');
  const viewDosen = document.getElementById('view-dosen');
  const viewSiswa = document.getElementById('view-siswa');
  
  const heroBadge = document.getElementById('hero-badge-text');
  const heroTitle = document.getElementById('hero-title');
  const heroSub = document.getElementById('hero-subtitle');

  const avatar = document.getElementById('user-avatar');
  const userName = document.getElementById('user-name');
  const userRole = document.getElementById('user-role');

  if (portalType === 'dosen') {
    document.body.className = 'theme-dosen';
    btnDosen.classList.add('active');
    btnSiswa.classList.remove('active');
    viewDosen.classList.add('active');
    viewSiswa.classList.remove('active');

    heroBadge.textContent = 'Portal Manajemen Ujian AI';
    heroTitle.textContent = 'Halo, Dr. Budi! 👋';
    heroSub.textContent = 'Asisten AI Otti siap membantu Anda merancang soal dan menilai jawaban siswa secara otomatis!';

    avatar.src = 'https://api.dicebear.com/7.x/bottts/svg?seed=DosenPro';
    userName.textContent = 'Dr. Budi Santoso, M.Kom';
    userRole.textContent = 'Dosen Pengampu';

    setOttiState('classic');
    showToast('Switched to Portal Dosen View');
  } else {
    document.body.className = 'theme-siswa';
    btnSiswa.classList.add('active');
    btnDosen.classList.remove('active');
    viewSiswa.classList.add('active');
    viewDosen.classList.remove('active');

    heroBadge.textContent = 'Portal Gamifikasi Siswa';
    heroTitle.textContent = 'Semangat Belajar, Siswa! 🚀';
    heroSub.textContent = 'Kerjakan quest ujian, kumpulkan XP, dan tingkatkan ranking leaderboard kamu bersama Otti!';

    avatar.src = 'https://api.dicebear.com/7.x/bottts/svg?seed=Kamu';
    userName.textContent = 'Kamu (Siswa)';
    userRole.textContent = 'Mahasiswa Teknik Informatika';

    setOttiState('classic');
    showToast('Switched to Portal Siswa View');
  }
}

// 4. HANDLE GENERATE EXAM (DOSEN)
async function handleGenerateExam(e) {
  e.preventDefault();
  const topic = document.getElementById('exam-topic').value;
  const count = document.getElementById('exam-count').value;

  // Set Otti into Loading/Generating state
  setOttiState('buat_soal');
  showToast(`Ottibot sedang menghubungi AI Agent untuk membuat ${count} soal tentang "${topic}"...`);

  const btnSubmit = document.getElementById('btn-submit-exam');
  btnSubmit.disabled = true;
  btnSubmit.innerHTML = `<i data-lucide="loader" class="spin"></i> Otti AI Agent Sedang Bekerja...`;

  try {
    const res = await fetch('http://localhost:5000/api/generate-exam', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ topic: topic, count: parseInt(count) })
    });
    
    const result = await res.json();
    setOttiState('classic');
    btnSubmit.disabled = false;
    btnSubmit.innerHTML = `<i data-lucide="sparkles"></i> Generate Ujian dengan Otti`;

    // Add log item
    const logStream = document.getElementById('otti-log-stream');
    if (logStream) {
      const now = new Date();
      const timeStr = now.toTimeString().substring(0, 5);
      const newLog = document.createElement('div');
      newLog.className = 'log-item';
      newLog.innerHTML = `<span class="log-time">${timeStr}</span><p>Otti AI Agent berhasil membuat <strong>${count} soal baru</strong> (Kode: ${result.exam_code || 'EX-NEW'}) tentang "${topic}".</p>`;
      logStream.prepend(newLog);
    }

    showToast(`Sukses! ${count} soal baru berhasil di-generate oleh AI Agent!`);
    if (window.lucide) lucide.createIcons();
  } catch (err) {
    console.error("Gagal panggil backend AI Agent:", err);
    setOttiState('classic');
    btnSubmit.disabled = false;
    btnSubmit.innerHTML = `<i data-lucide="sparkles"></i> Generate Ujian dengan Otti`;
    showToast(`Gagal menghubungi Backend/AI Agent. Pastikan app.py (port 5000) berjalan!`);
  }
}

// 5. SIMULATE GRADING & REVIEW
function simulateGrading() {
  setOttiState('menilai');
  showToast('Otti AI sedang memproses auto-grading...');

  setTimeout(() => {
    setOttiState('classic');
    showToast('Auto-grading selesai! 42 lembar jawaban telah diperiksa.');
  }, 2000);
}

function simulateReview(examName) {
  setOttiState('menilai');
  showToast(`Membuka hasil evaluasi AI untuk ${examName}...`);
}

// 6. STUDENT EXAM ANSWER SUBMISSION (CALL BACKEND AI AGENT)
async function submitStudentAnswer(quality) {
  const answerText = document.getElementById('student-answer-input').value;
  if (!answerText.trim()) {
    showToast('Harap isi jawaban kamu terlebih dahulu!');
    return;
  }

  setOttiState('menilai');
  showToast('Otti AI Agent sedang mengevaluasi jawabanmu...');

  try {
    const res = await fetch('http://localhost:5000/api/evaluate-answer', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        question_text: "Jelaskan perbedaan mendasar antara Data Structure Array dan Linked List serta kapan waktu yang tepat untuk menggunakannya!",
        student_answer: answerText,
        quality: quality
      })
    });

    const data = await res.json();
    const feedbackBox = document.getElementById('otti-feedback-box');
    const scoreVal = document.getElementById('result-score-val');
    const title = document.getElementById('result-title');
    const comment = document.getElementById('result-comment');

    feedbackBox.classList.remove('hidden', 'perfect', 'subpar');

    const scoreNum = data.score !== undefined ? Math.round(data.score) : (quality === 'perfect' ? 100 : 60);
    scoreVal.textContent = scoreNum;

    if (scoreNum >= 75) {
      setOttiState('nilai_bagus');
      feedbackBox.classList.add('perfect');
      title.textContent = 'Luar Biasa! Evaluasi Sempurna! 🎉';
      comment.textContent = `Otti AI Agent: "${data.reason || 'Jawaban kamu sangat komprehensif!'}"`;
      
      if (typeof confetti === 'function') {
        confetti({ particleCount: 100, spread: 70, origin: { y: 0.6 } });
      }
    } else {
      setOttiState('nilai_kurang');
      feedbackBox.classList.add('subpar');
      title.textContent = 'Hasil Evaluasi: Perlu Peningkatan 💡';
      comment.textContent = `Otti AI Agent: "${data.reason || 'Yuk tingkatkan pemahaman materi ini!'}"`;
    }

    showToast('Evaluasi dari AI Agent selesai!');
  } catch (err) {
    console.error("Gagal evaluate answer:", err);
    setOttiState('classic');
    showToast('Gagal menghubungi backend AI Agent (Flask port 5000).');
  }
}

// 7. TOAST NOTIFICATION UTILITY
function showToast(message) {
  const container = document.getElementById('toast-container');
  if (!container) return;

  const toast = document.createElement('div');
  toast.className = 'toast';
  toast.textContent = message;

  container.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transition = 'opacity 0.3s ease';
    setTimeout(() => toast.remove(), 300);
  }, 3000);
}

// 8. INITIALIZE PAGE ON LOAD
document.addEventListener('DOMContentLoaded', () => {
  setOttiState('classic');
  if (window.lucide) {
    lucide.createIcons();
  }
});
