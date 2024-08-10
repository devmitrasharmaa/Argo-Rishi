import os
import secrets
from flask import current_app, session
from flask import render_template, redirect, url_for, request, flash
from agrorishi.forms import LoginForm, RegistrationForm, UpdateAccountForm
from flask_login import login_user, current_user, logout_user, login_required
from agrorishi import app,db,bcrypt
from agrorishi.models import Farmers

from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required
import pyttsx3
import speech_recognition as sr
from deep_translator import GoogleTranslator
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from agrorishi import app



with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', title='DashBoard')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        farmer= Farmers.query.filter_by(email= form.email.data).first()
        if farmer and bcrypt.check_password_hash(farmer.password, form.password.data):
            login_user(farmer, remember= form.remember.data)
            next_page=request.args.get('next')
            flash("You've been logged in!", 'success')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash(f"Login Unsuccessful, check credentials!",'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pass = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        farmer = Farmers(
            username=form.username.data,
            password=hashed_pass,
            email=form.email.data
        )
        try:
            db.session.add(farmer)
            db.session.commit()
            flash("You're registered", 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash("Error registering user: " + str(e), 'danger')
    return render_template('register.html', title='Registration', form=form)

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    f_name, f_ext = os.path.splitext(form_picture.filename)
    picture_fname = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fname)

    try:
        form_picture.save(picture_path)
        print(f"Saved picture to {picture_path}")  # Debugging line
    except Exception as e:
        print(f"Error saving picture: {e}")

#     return picture_fname

@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file
        # Only update the image if a new one is provided
        elif not form.picture.data:
            # Do not update image_file if no new image is provided
            current_user.username = form.username.data
            current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account', image_file=image_file, form=form)



# Initialize LLaMA 3 model
model = OllamaLLM(model='llama3')
template = """
Answer the following question in Hindi

Here's the conversation history: {context}

Question: {question}

Answer:
"""
prompts = ChatPromptTemplate.from_template(template)
chain = prompts | model

# Text-to-speech function
def speak(text):
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[1].id)  # Assuming [1] is the female voice; change if necessary
    engine.setProperty('rate', 160)
    engine.say(text)
    engine.runAndWait()

# Speech recognizer
r = sr.Recognizer()

@app.route('/rishi_sahayog', methods=['GET', 'POST'])
@login_required
def rishi_sahayog():
    context = ''
    response = None
    selected_mode = 'type'  # Default mode
    
    if request.method == 'POST':
        selected_mode = request.form.get('mode')

        if selected_mode == 'speak':
            # Handle speech input
            user_input = get_user_input_from_speech()  # Implement speech recognition logic
            user_input = GoogleTranslator(source='auto', target='en').translate(user_input)
            print(f"Translated: {user_input}")
        else:
            # Handle text input
            user_input = request.form.get('user_input')
        
        if user_input:
            result = chain.invoke({'context': context, 'question': user_input})
            context += f"\nUser: {user_input}\nAI: {result}"

            if selected_mode == 'speak':
                speak(result)
            
            response = result
    
    return render_template('rishi_sahayog.html', title='Rishi Sahayog', selected_mode=selected_mode, response=response)

def get_user_input_from_speech():
    with sr.Microphone() as source:
        print("Listening to your voice....")
        speak("आपकी आवाज सुनी जा रही है")
        try:
            # Limiting the listening time to 15 seconds
            audio = r.listen(source, timeout=15, phrase_time_limit=15)
            command = r.recognize_google(audio, language='hi-IN')
            print(f"You said: {command}")
            return command
        except sr.WaitTimeoutError:
            speak("समय समाप्त हो गया है। कृपया फिर से बोलने का प्रयास करें।")
            print("Listening timed out. Please try speaking again.")
            return None
        except sr.UnknownValueError:
            speak("में आपकी आवाज समझ नहीं पा रहा हूं। कृपा फिर से बोलिए")
            print("Unrecognized Voice. Say that again, please.")
            return None



if __name__ == "__main__":
    app.run(debug=True)
