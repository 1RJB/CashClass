from your_application import db, create_app
from your_application.models import Flashcard

app = create_app()

with app.app_context():
    example_flashcards = [
        Flashcard(
            question="What is HTML?",
            answer="HTML stands for HyperText Markup Language.",
            user_id="user@example.com"  # Replace with the actual user email
        ),
        Flashcard(
            question="What is CSS?",
            answer="CSS stands for Cascading Style Sheets.",
            user_id="user@example.com"  # Replace with the actual user email
        ),
        Flashcard(
            question="What is JavaScript?",
            answer="JavaScript is a programming language used to create dynamic content on websites.",
            user_id="user@example.com"  # Replace with the actual user email
        )
    ]

    db.session.bulk_save_objects(example_flashcards)
    db.session.commit()
