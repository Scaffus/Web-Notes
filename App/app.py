from flask import Flask, redirect, url_for, render_template, flash, request
from flask_login import login_user, login_required, logout_user, current_user, LoginManager, UserMixin
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
    id         = db.Column(db.Integer, primary_key=True)
    content    = db.Column(db.String(2000))
    title      = db.Column(db.String(50))
    useruuid   = db.Column(db.String(36))

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
    
    return render_template('index.html', user=current_user)


@app.route('/login', methods=['GET', 'POST'])
def login():

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

    return render_template('login.html', user=current_user)


@app.route('/signup', methods=['GET', 'POST'])
def signup():

    if request.method == 'POST':

        username = request.form['name']
        password = request.form['password']
        mail     = request.form['mail'].lower()

        user = User.query.filter_by(mail=mail).first()

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
            newUser = User(username=username.lower(), mail=mail.lower(), password=generate_password_hash(password, method='sha256'), uuid=str(uuid.uuid4()))
            
            db.session.add(newUser)
            db.session.commit()

            login_user(newUser, remember=True)

            flash('Compte créé avec succès!', category='success')

        return redirect(url_for('login'))
    return render_template('signup.html', user=current_user)


@app.route('/signout')
@login_required
def signout():

    logout_user()

    return redirect(url_for('login'))


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
        useruuid  = current_user.uuid
        
        if len(title) < 2:
            flash('The title must be longer than 2 characters', category='error')
        elif len(content) < 2:
            flash('The content must be longer than 2 characters', category='error')
            
        else:
            new_note = Note(title=title, content=content, useruuid=useruuid)
            
            db.session.add(new_note)
            db.session.commit()

            flash('Note created, see it at \"My notes\".', category='success')
            
    return render_template('newNote.html', user=current_user)

@app.route('/notes')
@login_required
def notes():
    
    useruuid = request.args.get('uuid')
    
    notes = Note.query.filter_by(useruuid=useruuid)
    
    return render_template('notes.html', user=current_user, notes=notes) 


@app.route('/notes/<string:user_name>/edit/<int:note_id>', methods=['GET', 'POST'])
def edit_note(user_name, note_id):

    user_uuid = request.args.get('uuid')

    if request.method == 'POST':

        title   = request.form['title']
        content = request.form['content']

        if len(title) < 2:
            flash('The title must be longer than 2 characters', category='error')
        elif len(content) < 2:
            flash('The content must be longer than 2 characters', category='error')
            
        note = Note.query.get_or_404(note_id)

        if note.useruuid != user_uuid:
            flash('Error in the request, try to refresh the page.', category='error')
        else:

            note.title   = title
            note.content = content

            flash('Note \"' + note.title + '\" edited successfuly, see it at \"My notes\"', category='success')

            db.session.commit()
        
    note = Note.query.get_or_404(note_id)

    if note.useruuid != user_uuid:
        return 'Got an error :/'
    else:
        return render_template('editNote.html', user=current_user, note=note)


@app.route('/notes/<string:user_name>/delete/<int:note_id>')
def delete_note(user_name, note_id):

    user_uuid = request.args.get('uuid')

    if user_uuid != current_user.uuid:
        return 'Got an error :/ Wrong uuid'

    else:
        note = Note.query.get_or_404(note_id)

        db.session.delete(note)
        db.session.commit()

        flash('Note \"' + note.title + '\" deleted', category='success')

    return redirect('/notes?uuid=' + user_uuid)

if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)