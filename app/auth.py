import json
from flask import Blueprint, flash, render_template, request, url_for, redirect
from . import db
from .models import Users
from .forms import SignUp, Login
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
auth = Blueprint('auth', __name__)
from .models import Flashcard
from .models import QuizSubmission

auth = Blueprint('auth', __name__)

@auth.route('/flashcards')
@login_required
def flashcards():
    # Query the database for flashcards belonging to the current user
    user_flashcards = Flashcard.query.filter_by(user_id=current_user.email).all()
    
    # Convert flashcards to a list of dictionaries
    flashcards_data = [flashcard.to_dict() for flashcard in user_flashcards]
    
    # Render the template with the flashcards
    return render_template('flashcards.html', flashcards=flashcards_data)


@auth.route('/add_flashcard', methods=['GET', 'POST'])
@login_required
def add_flashcard():
    if request.method == 'POST':
        question = request.form.get('question')
        answer = request.form.get('answer')
        category = request.form.get('category')
        
        new_flashcard = Flashcard(
            question=question,
            answer=answer,
            category=category,
            user_id=current_user.email
        )
        db.session.add(new_flashcard)
        db.session.commit()
        flash('Flashcard added successfully!', 'success')
        return redirect(url_for('auth.flashcards'))
    
    return render_template('add_flashcard.html')


@auth.route('/lesson_home')
@login_required
def lesson_home():
    return render_template('lesson_home.html')

@auth.route('/')
def home():
    if current_user.is_active:
        return render_template("home.html", name_user=current_user.name)
    return render_template("home.html")

@auth.route('/signup', methods=['GET','POST'])
def signup():
    # insert code here
    if current_user.is_active:
        return redirect(url_for("views.show_expenses"))

    form = SignUp(request.form)
    if form.validate_on_submit():
        name = form.name.data.strip() if form.name.data.strip() else ''
        new_user = Users(name=name, email=form.email.data.lower(), password=generate_password_hash(form.password.data))
        db.session.add(new_user)
        db.session.commit()

        flash('Account created!', category='success')
        return redirect(url_for('auth.login'))

    return render_template("signup.html", form=form)


@auth.route('/login', methods=['GET','POST'])
def login():
    # insert code here
    if current_user.is_active:
        return redirect(url_for("views.show_expenses"))

    form = Login(request.form)
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data.lower()).first()

        if user:
            if check_password_hash(user.password, form.password.data):
                flash('Logged in successfully', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.show_expenses'))
        
            else:
                flash('Incorrect password, please try again.', category='error')
        else:
            flash('No account with that email address.', category='error')

    return render_template('login.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.home'))

import anthropic

# Initialize Anthropic client
client = anthropic.Anthropic()

def get_quiz():
    try:
        # Generate quiz text using the Anthropic API
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": 'DO NOT EVER RESPOND IN ANYTHING OTHER THAN JSON FORMAT. JUST GIVE ME IN THE JSON RESPONSE. Give 5 multiple choice questions for my quiz. The quiz aims to improve a regularly financial illiterate 18 to 24 year old in Singapore\'s financial literacy. Each question should be followed by four multiple-choice options. Give the questions in JSON format only, using double quotes in JSON FORMAT: { "1": { "question": "<question goes here>", "answers": { "A": "<Option 1 goes here>", "B": "<Option 2 goes here>", "C": "<Option 3 goes here>", "D": "<Option 4 goes here>" }, "answer": "A" }, "2": { "question": "<question goes here>", "answers": { "A": "<Option 1 goes here>", "B": "<Option 2 goes here>", "C": "<Option 3 goes here>", "D": "<Option 4 goes here>", }, "answer": "B" } }\n MAKE SURE ALWAYS ANSWER IN JSON FORMAT'
                }
            ]
        )
        quiz_text = response.content[0].text.strip()
        print("Generated Quiz Text:", quiz_text)  # Debugging line
        
        # Parse the quiz data
        quiz_data = parse_quiz_data(quiz_text)
         # Assign IDs to the questions
        for idx, question in enumerate(quiz_data, start=1):
            question['id'] = idx  # Set the question ID for reference in the form
        print("Parsed Quiz Data:", quiz_data)  # Debugging line
        return quiz_data
    except Exception as e:
        print(f"Error fetching quiz data: {e}")
        return []

def parse_quiz_data(quiz_text):
    try:
        # Remove any leading/trailing whitespace and newlines
        quiz_text = quiz_text.strip()
        
        # If the text is wrapped in code blocks, remove them
        if quiz_text.startswith("```") and quiz_text.endswith("```"):
            quiz_text = quiz_text[3:-3].strip()
        
        # Parse the JSON-like string into a Python dictionary
        quiz_dict = json.loads(quiz_text.replace("'", '"'))
        
        # Convert the dictionary into the desired format
        quiz = []
        for idx, question_data in quiz_dict.items():
            question = {
                'id': idx,  # Assign the ID based on the dictionary key
                'question': question_data['question'],
                'options': [question_data['answers'][key] for key in 'ABCD'],
                'correct_answer': question_data['answer']  # Include the correct answer
            }
            quiz.append(question)
        
        return quiz
    except json.JSONDecodeError as e:
        print(f"Error parsing quiz data: {e}")
        return []

@auth.route('/quiz', methods=['GET', 'POST'])
@login_required
def quiz():
    quiz = get_quiz()  # Retrieve or generate the quiz
    
    if request.method == 'POST':
        user_answers = request.form.to_dict()
        correct_count = 0

        for question in quiz:
            question_id = question['id']
            selected_answer = user_answers.get(str(question_id))
            question['selected'] = selected_answer
            question['is_correct'] = (selected_answer == question['correct_answer'])
            if question['is_correct']:
                correct_count += 1

        # Save the quiz submission
        quiz_submission = QuizSubmission(
            user_id=current_user.email,
            quiz_data=json.dumps(quiz),  # Serialize the quiz data as JSON
            score=correct_count
        )
        db.session.add(quiz_submission)
        db.session.commit()

        flash(f"You got {correct_count} out of {len(quiz)} correct!", "success")

    return render_template('quiz.html', quiz=quiz)

@auth.route('/quiz_submissions')
@login_required
def quiz_submissions():
    submissions = QuizSubmission.query.filter_by(user_id=current_user.email).all()
    return render_template('quiz_submissions.html', submissions=submissions, json=json)

@auth.route('/quiz_submission/<int:submission_id>')
@login_required
def quiz_submission(submission_id):
    submission = QuizSubmission.query.get_or_404(submission_id)
    if submission.user_id != current_user.email:
        flash("You are not authorized to view this quiz submission.", "error")
        return redirect(url_for('auth.quiz_submissions'))

    quiz = json.loads(submission.quiz_data)  # Deserialize the quiz data from JSON
    return render_template('quiz_submission.html', quiz=quiz, score=submission.score, submitted_at=submission.submitted_at)

@auth.route('/lesson1')
def lesson1():
    return render_template('lesson1.html', lesson1=lesson1)

@auth.route('/lesson2')
def lesson2():
    return render_template('lesson2.html', lesson2=lesson2)

@auth.route('/lesson3')
def lesson3():
    return render_template('lesson3.html', lesson3=lesson3)

@auth.route('/lesson4')
def lesson4():
    return render_template('lesson4.html', lesson4=lesson4)

