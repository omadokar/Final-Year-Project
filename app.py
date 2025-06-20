from flask import Flask, request, render_template, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from pymongo import MongoClient
import pandas as pd
import joblib

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MongoDB Atlas Configuration
MONGO_URI = "mongodb+srv://angrybird081003:6gbjWprDqqRS6jzm@cluster0.ncf72gj.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"  # Replace this with your actual MongoDB URI
client = MongoClient(MONGO_URI)
db = client['user_data']
users_collection = db['users']
career_collection = db['career_history']

# Load model and encoders
model = joblib.load('career_model.pkl')
le = joblib.load('label_encoder.pkl')
career_df = pd.read_csv('Data_final.csv')

questions = {
    "O_score": ["I enjoy trying new experiences.", "I like thinking about abstract ideas.",
                 "I prefer variety over routine.", "I am highly imaginative.", "I am open to different perspectives."],
    "C_score": ["I stick to my plans and schedules.", "I complete tasks on time.",
                "I am highly organized.", "I work hard to achieve my goals.", "I pay attention to details."],
    "E_score": ["I enjoy socializing with people.", "I prefer working in a team.",
                "I feel comfortable speaking in front of groups.", "I am energetic and talkative.", "I like to take charge."],
    "A_score": ["I easily empathize with others.", "I like helping others.",
                "I am patient and cooperative.", "I work well in a team.", "I am kind and considerate."],
    "N_score": ["I often feel anxious or nervous.", "I get stressed easily.",
                "I overthink small problems.", "I experience mood swings.", "I find it hard to stay calm under pressure."],
    "Numerical_Aptitude": ["I enjoy solving math problems.", "I am comfortable with numbers.",
                            "I can analyze numerical data easily.", "I like solving logical puzzles.", "I am good at mental calculations."],
    "Spatial_Aptitude": ["I can visualize objects in 3D easily.", "I enjoy puzzles involving shapes.",
                         "I can easily read maps and diagrams.", "I have good hand-eye coordination.", "I like working with design or architecture."],
    "Perceptual_Aptitude": ["I notice small details quickly.", "I can spot patterns easily.",
                             "I am good at identifying differences between images.", "I work well under time pressure.", "I enjoy activities that require quick thinking."],
    "Abstract_Reasoning": ["I can identify patterns in complex data.", "I enjoy problem-solving activities.",
                           "I am good at recognizing trends.", "I can understand complex concepts quickly.", "I think logically and analytically."],
    "Verbal_Reasoning": ["I enjoy reading and writing.", "I can understand complex texts easily.",
                         "I can summarize information well.", "I have a good vocabulary.", "I am good at understanding meanings from context."]
}

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])

        if users_collection.find_one({"email": email}):
            flash("Email already registered.", 'danger')
            return redirect(url_for('register'))

        users_collection.insert_one({"name": name, "email": email, "password": password})
        flash("Registration successful! Please log in.", 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = users_collection.find_one({"email": email})

        if user and check_password_hash(user['password'], password):
            session['user_id'] = str(user['_id'])
            session['name'] = user['name']
            session['email'] = user['email']

            if user['email'] == 'nextgen@gmail.com':
                return redirect(url_for('admin_panel'))
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid credentials.", 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))

@app.route('/admin')
def admin_panel():
    if 'user_id' not in session or session['email'] != 'nextgen@gmail.com':
        flash("Access denied!", "danger")
        return redirect(url_for('login'))

    users = list(users_collection.find())
    data = []
    for user in users:
        career = career_collection.find_one({"user_id": str(user['_id'])})
        data.append({
            "name": user['name'],
            "email": user['email'],
            "career_prediction": career['career_prediction'] if career else "-"
        })
    return render_template('admin.html', users=data)

@app.route('/dash')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    history = career_collection.find({"user_id": session['user_id']})
    return render_template('dash.html', name=session['name'], history=history)

@app.route('/take_test', methods=['GET', 'POST'])
def take_test():
    if request.method == 'GET':
        return render_template('take_test.html', questions=questions)

    scores = {}
    try:
        for key in questions.keys():
            responses = [int(request.form.get(f'{key}_{i}', 0)) for i in range(5)]
            scores[key] = sum(responses)

        if sum(scores.values()) == 0:
            return "Please recalculate the answers."

        input_data = list(scores.values())
        prediction = model.predict([input_data])
        career = le.inverse_transform(prediction)[0]

        career_collection.insert_one({
            "user_id": session['user_id'],
            "career_prediction": career
        })

        flash("Test submitted successfully!", "success")
        return redirect(url_for('dashboard'))

    except Exception as e:
        return f"Error processing the form: {str(e)}"

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/contri')
def contri():
    return render_template('contri.html')

@app.route('/chat')
def chat():
    return render_template('chat.html')

if __name__ == '__main__':
    app.run(debug=True)
