import json
from flask import Blueprint, flash, render_template, request, url_for, redirect
from . import db
from .models import Users
from .forms import SignUp, Login
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
auth = Blueprint('auth', __name__)
import yfinance as yf
import datetime
from bokeh.plotting import figure, show, output_file
from bokeh.embed import components 
from bokeh.resources import CDN
from .models import Flashcard
import anthropic

@auth.route('/flashcards')
@login_required
def flashcards():
    # Query the database for flashcards belonging to the current user
    user_flashcards = Flashcard.query.filter_by(user_id=current_user.email).all()
    
    # Render the template with the flashcards
    return render_template('flashcards.html', flashcards=user_flashcards)

@auth.route('/lesson_home')
@login_required
def lesson_home():
    return render_template('lesson_home.html')


@auth.route('/plot')
def plot():
    start = datetime.datetime(2021, 10, 1)
    end = datetime.datetime(2024, 9, 1)

    df = yf.download("GOOG", start=start, end=end)

    def inc_dec(c, o):
        if c > o:
            value = "Increase"
        elif c < o:
            value = "Decrease"
        else:
            value = "Equal"
        return value

    df["Status"] = [inc_dec(c, o) for c, o in zip(df.Close, df.Open)]
    df["Middle"] = (df.Open+df.Close)/2
    df["Height"] = abs(df.Close-df.Open)

    p = figure(x_axis_type='datetime', width=1000, height=300, sizing_mode="scale_width")
    p.title = "Candlestick Chart"
    p.grid.grid_line_alpha = 0.3

    hours_12 = 12*60*60*1000

    p.segment(df.index, df.High, df.index, df.Low, color="black")

    p.rect(df.index[df.Status == "Increase"], df.Middle[df.Status == "Increase"],
           hours_12, df.Height[df.Status == "Increase"], fill_color="#CCFFFF", line_color="black")

    p.rect(df.index[df.Status == "Decrease"], df.Middle[df.Status == "Decrease"],
           hours_12, df.Height[df.Status == "Decrease"], fill_color="#FF3333", line_color="black")

    script1, div1 = components(p)
    cdn_js = CDN.js_files[0]
    print(df)
    return render_template("plot.html", script1=script1, div1=div1, cdn_js=cdn_js)

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
                    "content": 'DO NOT RESPOND IN ANYTHING OTHER THAN JSON FORMAT. JUST GIVE ME THE JSON RESPONSE. Give 5 multiple choice questions for my quiz. The quiz aims to improve a regularly financial illiterate 18 to 24 year old in Singapore\'s financial literacy. Each question should be followed by four multiple-choice options. Give the questions in this format, using double quotes: { "1": { "question": "<question goes here>", "answers": { "A": "<Option 1 goes here>", "B": "<Option 2 goes here>", "C": "<Option 3 goes here>", "D": "<Option 4 goes here>" } }, "2": { "question": "<question goes here>", "answers": { "A": "<Option 1 goes here>", "B": "<Option 2 goes here>", "C": "<Option 3 goes here>", "D": "<Option 4 goes here>" } } }'
                }
            ]
        )
        quiz_text = response.content[0].text.strip()
        print("Generated Quiz Text:", quiz_text)  # Debugging line
        
        # Parse the quiz data
        quiz_data = parse_quiz_data(quiz_text)
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
        for _, question_data in quiz_dict.items():
            question = {
                'question': question_data['question'],
                'options': [question_data['answers'][key] for key in 'ABCD']
            }
            quiz.append(question)
        
        return quiz
    except json.JSONDecodeError as e:
        print(f"Error parsing quiz data: {e}")
        return []

@auth.route('/quiz')
def quiz():
    quiz = get_quiz()
    return render_template('quiz.html', quiz=quiz)

@auth.route('/lesson_home.html')
def lesson_main():
    return render_template('lesson_home.html', lesson_main=lesson_main )

@auth.route('/lesson1.html')
def lesson1():
    return render_template('lesson1.html', lesson1=lesson1)