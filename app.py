from flask import Flask, request, render_template, redirect, url_for, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

from ml_dependencies import vectorizer, model

app = Flask(__name__)
app.config['SECRET_KEY'] = 'b7N0hMOcrg2lC3hwi7EGWQ'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

    def check_password(self, password):
        return self.password == password

class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref=db.backref('histories', lazy=True))
    input_text = db.Column(db.String(200), nullable=False)
    prediction = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user:
            return render_template('signup.html', error='Username already exists')
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        text = request.form['news_text']
        vectorized_text = vectorizer.transform([text])
        prediction = int(model.predict(vectorized_text)[0])
        if current_user.is_authenticated:
            history = History(user_id=current_user.id, input_text=text, prediction=prediction)
            db.session.add(history)
            db.session.commit()
        else:
            if 'history' not in session:
                session['history'] = []
            session['history'].append({'input_text': text, 'prediction': prediction})
            session.modified = True
    recent_history = None
    if current_user.is_authenticated:
        recent_history = History.query.filter_by(user_id=current_user.id).order_by(History.id.desc()).first()
        recent_history = {'input_text': recent_history.input_text, 'prediction': recent_history.prediction}
    else:
        if 'history' in session:
            recent_history = session['history'][-1]
    
    if recent_history:
        return render_template('home.html', recent_history=recent_history)
    return render_template('home.html')

# @app.route('/predict', methods=['POST'])
# def predict():
#     text = request.form['news_text']
#     vectorized_text = vectorizer.transform([text])
#     prediction = int(model.predict(vectorized_text)[0])
#     if current_user.is_authenticated:
#         history = History(user_id=current_user.id, input_text=text, prediction=prediction)
#         db.session.add(history)
#         db.session.commit()
#     else:
#         if 'history' not in session:
#             session['history'] = []
#         session['history'].append({'input_text': text, 'prediction': prediction})
#     # return render_template('predict.html', news_text=text, result=prediction)

@app.route('/history')
def history():
    if current_user.is_authenticated:
        histories = History.query.filter_by(user_id=current_user.id).all()
        histories = [{'input_text': history.input_text, 'prediction': history.prediction} for history in histories]
        return render_template('history.html', histories=histories)
    elif 'history' in session:
        return render_template('history.html', histories=session['history'])
    return redirect(url_for('index'))

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
