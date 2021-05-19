from flask import Flask, redirect, url_for, render_template, flash, request
from flask_login import login_manager, login_user, login_required, logout_user, current_user, LoginManager, UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
import uuid

app = Flask(__name__)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database/database.db'
app.config['SECRET_KEY'] = '16a627a9-a69b-4b07-9836-5b8b32b1fdc0'

db = SQLAlchemy(app)
SQLALCHEMY_TRACK_MODIFICATIONS = False

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(mail):

    return User.query.get(mail)

class Note(db.Model):
    id       = db.Column(db.Integer, primary_key=True)
    content  = db.Column(db.String(2000))
    title    = db.Column(db.String(50))

class User(db.Model, UserMixin):
    id       = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80))
    mail     = db.Column(db.String(120))
    password = db.Column(db.String(80))
    uuid     = db.Column(db.String(36))

    def is_active(self):
        return True

    def is_authenticated(self):
        return self.authenticated

    def is_anonymous(self):
        return False
    
@app.route('/')
def index():
    
    return render_template('index.html')


@app.route('/signin', methods=['GET', 'POST'])
def signin():

    if request.method == 'POST':

        mail     = request.form['mail']
        password = request.form['password']

        user = User.query.filter_by(mail=mail).first()

        if user:
            if check_password_hash(user.password, password):
                flash('Vous avez été connecté avec succès!', category='success')
                login_user(user, remember=True)

                return redirect(url_for('index'))

            else:
                flash('Le mot de passe est incorrect.', category='error')
        else:
            flash('L\'addresse email n\'existe pas.')

    return render_template('signin.html', user=current_user)


@app.route('/signup', methods=['GET', 'POST'])
def signup():

    if request.method == 'POST':

        username = request.form['name']
        password = request.form['password']
        mail     = request.form['mail']
        uuid     = uuid.uuid4()

        user = User.query.filter_by(mail=mail.lower()).first()

        if user:
            flash('L\'addresse email existe déjà.', category='error')
            return redirect(url_for('signup'))

        elif len(username) < 3:
            flash('Le pseudonyme doit contennir plus de 2 caractères.', category='error')
            return redirect(url_for('signup'))

        elif len(password) < 8:
            flash('Le mot de passe doit faire au moins 8 caractères.', category='error')
            return redirect(url_for('signup'))
            
        elif len(mail) < 4:
            flash('L\'addresse mail doit contennir plus de 3 caractères.', category='error')
            return redirect(url_for('signup'))

        else:
            newUser = User(username=username.lower(), mail=mail.lower(), password=generate_password_hash(password, method='sha256'), uuid=uuid)
            
            db.session.add(newUser)
            db.session.commit()

            login_user(newUser, remember=True)

            flash('Compte créé avec succès!', category='success')

        return redirect(url_for('signin'))
    return render_template('signup.html', user=current_user)


@app.route('/signout')
@login_required
def signout():

    logout_user()

    return redirect(url_for('signin'))


@app.route('/account')
@login_required
def account():
    
    return render_template('account.html', user=current_user)


@app.route('/new', methods=['GET', 'POST'])
@login_required
def new_note():
    
    if request.method == 'POST':
        
        title   = request.form['title']
        content = request.form['content']
        
        if not title or title.len() < 2:
            flash('The title must be longer than 2 characters', category='error')
        elif not content or content < 2:
            flash('The content must be longer than 2 characters', category='error')
        else:
            
            new_note = Note(title=title, content=content)
            

@app.route('/notes')
@login_required
def notes():
    
    notes = Note.query.get()

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)