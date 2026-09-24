-- Schema Database Supabase untuk Smart-Test AI
-- 6 Tabel: teachers, materials, exams, questions, student_submissions, grade_appeals

-- 1. Table: teachers
CREATE TABLE IF NOT EXISTS teachers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    email TEXT UNIQUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. Table: materials
CREATE TABLE IF NOT EXISTS materials (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    teacher_id UUID REFERENCES teachers(id) ON DELETE SET NULL,
    title TEXT NOT NULL,
    file_url TEXT,
    content_text TEXT,
    jumlah_pg INT DEFAULT 5,
    jumlah_essai INT DEFAULT 2,
    level_distribution JSONB DEFAULT '{"C1":0, "C2":0, "C3":0, "C4":100}'::jsonb,
    status TEXT DEFAULT 'processing' CHECK (status IN ('processing', 'generated', 'failed')),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Table: exams
CREATE TABLE IF NOT EXISTS exams (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    material_id UUID REFERENCES materials(id) ON DELETE SET NULL,
    teacher_id UUID REFERENCES teachers(id) ON DELETE SET NULL,
    title TEXT NOT NULL,
    teacher_name TEXT,
    exam_code VARCHAR(10) UNIQUE NOT NULL,
    duration_minutes INT DEFAULT 60,
    questions_shown_per_student INT DEFAULT 5,
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'closed')),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. Table: questions
CREATE TABLE IF NOT EXISTS questions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    material_id UUID REFERENCES materials(id) ON DELETE CASCADE,
    exam_id UUID REFERENCES exams(id) ON DELETE CASCADE,
    question_type TEXT CHECK (question_type IN ('pg', 'essai')),
    question_text TEXT NOT NULL,
    options JSONB DEFAULT '[]'::jsonb,
    correct_answer TEXT,
    rubric_essay TEXT,
    difficulty_level TEXT DEFAULT 'C4',
    status TEXT DEFAULT 'draft' CHECK (status IN ('draft', 'approved')),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. Table: student_submissions
CREATE TABLE IF NOT EXISTS student_submissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    exam_id UUID REFERENCES exams(id) ON DELETE CASCADE,
    student_name TEXT NOT NULL,
    student_nis TEXT,
    answers JSONB DEFAULT '[]'::jsonb,
    pg_score FLOAT DEFAULT 0,
    essay_draft_score FLOAT DEFAULT 0,
    total_score FLOAT DEFAULT 0,
    status TEXT DEFAULT 'pending_review' CHECK (status IN ('pending_review', 'published')),
    submitted_at TIMESTAMPTZ DEFAULT NOW()
);

-- 6. Table: grade_appeals
CREATE TABLE IF NOT EXISTS grade_appeals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    submission_id UUID REFERENCES student_submissions(id) ON DELETE CASCADE,
    student_reason TEXT NOT NULL,
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected')),
    teacher_notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
