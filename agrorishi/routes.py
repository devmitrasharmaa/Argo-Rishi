import os
import secrets
from flask import abort,Blueprint, current_app, session, render_template, redirect, url_for, request, flash
from flask_login import login_user, current_user, logout_user, login_required
from . import app, db, bcrypt
from .predict import predict_disease
from .models import Farmers, Post
from .forms import LoginForm, PostForm, RegistrationForm, UpdateAccountForm
from PIL import Image
import pyttsx3
import speech_recognition as sr
from deep_translator import GoogleTranslator
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from flask_socketio import SocketIO, emit
import random
import time
from threading import Thread, Event
main = Blueprint('main', __name__)
socketio = SocketIO(app)

thread = Thread()
thread_stop_event = Event()

with app.app_context():
    db.create_all()

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', title='Dashboard')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        farmer = Farmers.query.filter_by(email=form.email.data).first()
        if farmer and bcrypt.check_password_hash(farmer.password, form.password.data):
            login_user(farmer, remember=form.remember.data)
            next_page = request.args.get('next')
            flash("You've been logged in!", 'success')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash(f"Login Unsuccessful, check credentials!", 'danger')
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

    return picture_fname

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
You are an Indian agricultural expert. You give answers in Hindi.

Here's the conversation history: {context}

Question: {question}

Answer:
"""
prompts = ChatPromptTemplate.from_template(template)
chain = prompts | model

# Remove the Text-to-Speech function
# def speak(text):
#     engine = pyttsx3.init()
#     voices = engine.getProperty('voices')
#     engine.setProperty('voice', voices[1].id)  # Assuming [1] is the female voice; change if necessary
#     engine.setProperty('rate', 160)
#     engine.say(text)
#     engine.runAndWait()

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
            user_input = get_user_input_from_speech()
        else:
            # Handle text input
            user_input = request.form.get('user_input')
        
        if user_input:
            result = chain.invoke({'context': context, 'question': user_input})
            context += f"\nUser: {user_input}\nAI: {result}"

            # Print the result in the response
            response = result
    
    return render_template('rishi_sahayog.html', title='Rishi Sahayog', selected_mode=selected_mode, response=response)

def get_user_input_from_speech():
    with sr.Microphone() as source:
        print("Listening to your voice....")
        # Removed the speak call for speech input
        try:
            # Limiting the listening time to 15 seconds
            audio = r.listen(source, timeout=15, phrase_time_limit=15)
            command = r.recognize_google(audio, language='hi-IN')
            print(f"You said: {command}")
            return command
        except sr.WaitTimeoutError:
            print("Listening timed out. Please try speaking again.")
            return None
        except sr.UnknownValueError:
            print("Unrecognized Voice. Say that again, please.")
            return None


@app.route("/community")
def community():
    posts = Post.query.order_by(Post.upvotes.desc()).all()
    return render_template('community.html', posts=posts)

def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/post_pics', picture_fn)

    output_size = (500, 500)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        picture_file = save_picture(form.picture.data)
        post = Post(
            image_file=picture_file,
            caption=form.caption.data,
            description=form.description.data,  # Assuming form has this field
            category=form.category.data,  # Assuming form has this field
            author=current_user
        )
        db.session.add(post)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('community'))
    return render_template('create_post.html', title='New Post', form=form)

@app.route("/post/<int:post_id>/upvote", methods=['POST'])
@login_required
def upvote(post_id):
    post = Post.query.get_or_404(post_id)
    post.upvotes += 1
    db.session.commit()
    return redirect(url_for('community'))

@app.route("/my_posts")
@login_required
def user_posts():
    posts = Post.query.filter_by(user_id=current_user.id).all()
    return render_template('user_posts.html', posts=posts)

@app.route("/delete_post/<int:post_id>", methods=['POST'])
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.user_id != current_user.id:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Your post has been deleted!', 'success')
    return redirect(url_for('user_posts'))

def generate_sample_data():
    while not thread_stop_event.is_set():
        # Generate sample data for soil moisture, temperature, and humidity
        soil_moisture = round(random.uniform(30, 60), 2)
        temperature = round(random.uniform(20, 35), 2)
        humidity = round(random.uniform(40, 70), 2)
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')

        print(f'Data generated - Time: {timestamp}, Soil Moisture: {soil_moisture}, Temperature: {temperature}, Humidity: {humidity}')

        # Emit the generated data to the client
        socketio.emit('sensor_update', {
            'timestamp': timestamp,
            'soil_moisture': soil_moisture,
            'temperature': temperature,
            'humidity': humidity
        })

        time.sleep(2)  # Adjust this for how often you want to generate new data

@app.route('/sensorwala')
def sensorwala():
    return render_template('index_sensor.html')  # The page to display sensor data

@socketio.on('connect')
def handle_connect(sid):
    global thread
    if not thread.is_alive():
        thread = Thread(target=generate_sample_data)
        thread.start()

@socketio.on('disconnect')
def handle_disconnect(sid):
    # Stop the sample data thread if it is running
    if thread.is_alive():
        thread_stop_event.set()
        thread.join()
        thread_stop_event.clear()

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        # Check if the file is part of the POST request
        file = request.files['image']
        if file:
            # Define the upload folder path
            upload_folder = os.path.join("static", "uploads")
            
            # Ensure the uploads directory exists
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            
            # Save the uploaded file
            image_path = os.path.join(upload_folder, file.filename)
            file.save(image_path)

            # Make prediction (assuming you have the predict_disease function)
            disease_name, img_rgb = predict_disease(image_path)

            # Display results on a new page
            return render_template('result.html', disease_name=disease_name, image_path=image_path)

    return render_template('upload.html')
