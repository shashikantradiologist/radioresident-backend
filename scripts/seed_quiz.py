# scripts/seed_quiz.py
from app import create_app
from app.models.user import db
from app.models.quiz import Quiz, Question

QUESTIONS = [
    {
        "prompt": "On a PA chest radiograph, the right heart border is formed by:",
        "A": "Right atrium",
        "B": "Right ventricle",
        "C": "Left atrium",
        "D": "Left ventricle",
        "correct": "A",
        "explanation": "Right heart border on PA view is mainly right atrium."
    },
    {
        "prompt": "The silhouette sign helps localize lung pathology because it depends on:",
        "A": "Air bronchograms",
        "B": "Loss of normal interface between two structures of same density",
        "C": "Hyperinflation",
        "D": "Rib notching",
        "correct": "B",
        "explanation": "Silhouette sign occurs when adjacent structures of similar density lose their border."
    },
    {
        "prompt": "Free intraperitoneal air is best seen on erect chest radiograph as:",
        "A": "Air-fluid level in stomach",
        "B": "Air under diaphragm",
        "C": "Central bowel gas",
        "D": "Rigler sign only",
        "correct": "B",
        "explanation": "Erect CXR can show pneumoperitoneum as air under diaphragm."
    },
    {
        "prompt": "On non-contrast CT brain, acute hemorrhage is typically:",
        "A": "Hypodense",
        "B": "Isodense",
        "C": "Hyperdense",
        "D": "Invisible",
        "correct": "C",
        "explanation": "Acute blood is usually hyperdense on NCCT."
    },
    {
        "prompt": "Which is the earliest CT sign of MCA infarct?",
        "A": "Ring enhancement",
        "B": "Hyperdense MCA sign",
        "C": "Calcification",
        "D": "Vasogenic edema only",
        "correct": "B",
        "explanation": "Hyperdense MCA sign is an early sign of thrombus."
    },
    {
        "prompt": "Most common site for aspiration pneumonia in supine patient:",
        "A": "Right upper lobe anterior segment",
        "B": "Right lower lobe superior segment",
        "C": "Left upper lobe apicoposterior segment",
        "D": "Lingula",
        "correct": "B",
        "explanation": "Supine aspiration: posterior upper lobes and superior segments of lower lobes (often right)."
    },
    {
        "prompt": "A 'double wall' (Rigler) sign indicates:",
        "A": "Pleural effusion",
        "B": "Pneumothorax",
        "C": "Pneumoperitoneum",
        "D": "Bowel obstruction",
        "correct": "C",
        "explanation": "Rigler sign = air on both sides of bowel wall in pneumoperitoneum."
    },
    {
        "prompt": "The left heart border on PA chest radiograph is primarily formed by:",
        "A": "Left atrium",
        "B": "Pulmonary artery",
        "C": "Left ventricle",
        "D": "Aorta only",
        "correct": "C",
        "explanation": "Left heart border is mainly left ventricle."
    },
    {
        "prompt": "Midline shift on CT brain is best described as shift of:",
        "A": "Falx cerebri",
        "B": "Septum pellucidum from midline",
        "C": "Cerebellar vermis",
        "D": "Basilar artery",
        "correct": "B",
        "explanation": "Classically measured at septum pellucidum level."
    },
    {
        "prompt": "On abdominal radiograph, multiple central air-fluid levels with valvulae conniventes suggests:",
        "A": "Large bowel obstruction",
        "B": "Small bowel obstruction",
        "C": "Ileus",
        "D": "Ascites",
        "correct": "B",
        "explanation": "Central loops + valvulae conniventes = SBO."
    },
]

def run():
    app = create_app()
    with app.app_context():
        existing = Quiz.query.filter_by(title="10 Marks Radiology Drill").first()
        if existing:
            print("Quiz already exists:", existing.id)
            return

        quiz = Quiz(title="10 Marks Radiology Drill", is_active=True)
        db.session.add(quiz)
        db.session.flush()

        for q in QUESTIONS:
            db.session.add(Question(
                quiz_id=quiz.id,
                prompt=q["prompt"],
                option_a=q["A"],
                option_b=q["B"],
                option_c=q["C"],
                option_d=q["D"],
                correct=q["correct"],
                explanation=q.get("explanation"),
                is_active=True,
            ))

        db.session.commit()
        print("Seeded quiz id:", quiz.id)

if __name__ == "__main__":
    run()