import hashlib
import datetime
import logging
from .. import mail
from flask_mail import Message
from Models.user_model import User, db
from Models.explanation_model import Explanation
from Models.category_model import Category
from Models.subject_model import Subject
from flask import Blueprint, abort, flash, render_template, redirect, request, url_for, session

user_bp = Blueprint("user", __name__, template_folder="templates/users")
logger = logging.getLogger(__name__)

# Main Page
@user_bp.route('/')
def index():
    
    if 'user_id' in session:
        if session['user_role'] != 3:
            abort(403) 
            
    categories = Category.query.all()
    subjects = Subject.query.all()
    explanation = Explanation.query.filter(Explanation.id == 2031).first()
        
    return render_template('test.html', categories = categories, subjects = subjects, explanation = explanation)



@user_bp.route('/addUser', methods=['GET','POST'])
def addUser():
    
    if 'user_id' in session:
        if session['user_role'] != 3:
            abort(403) 
    
    if request.method == 'POST':
        
        # Get data from form
        name = request.form.get('name')
        username = request.form.get('username')  
        email = request.form.get('email')
        password = request.form.get('password')
        
        # Check whether username already exists or not
        user = User.query.filter_by(
                                Username = username,
                                ).first()
        
        # if user already exists
        if user:
            flash("Username already exists.", "message")
            return redirect(url_for('user.addUser'))
        
        
        # if new user
        new_user = User(
            Name = name, 
            Username=username, 
            Password=hashlib.sha256(password.encode()).hexdigest(), 
            Email=email, 
            RoleId=3,
            JoinDate = datetime.datetime.now())
        
        db.session.add(new_user)
        db.session.commit()
        # Send email to contributor
        
        
        msg = Message("Welcome to the Contributor Community!",
                      sender = "bizintro1@gmail.com",
                  recipients=[email])
        msg.html = f"""<!DOCTYPE html>
                                <html>
                                <head>
                                    <meta charset="UTF-8">
                                    <title>Welcome to Our Community</title>
                                    <style>
                                        body {{
                                            font-family: Arial, sans-serif;
                                            background-color: #f7f7f7;
                                            margin: 0;
                                            padding: 0;
                                        }}
                                        .container {{
                                            max-width: 600px;
                                            margin: 0 auto;
                                            padding: 20px;
                                            background-color: #fff;
                                            border-radius: 10px;
                                            box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.1);
                                        }}
                                        .header {{
                                            background-color: #007bff;
                                            color: #fff;
                                            text-align: center;
                                            padding: 10px;
                                            border-top-left-radius: 10px;
                                            border-top-right-radius: 10px;
                                        }}
                                        .message {{
                                            padding: 20px;
                                        }}
                                    </style>
                                </head>
                                <body>
                                    <div class="container">
                                        <div class="header">
                                            <h1>Welcome to Our Community</h1>
                                        </div>
                                        <div class="message">
                                            <p>Hi <b>{ name }</b>,</p>
                                            <p>You have been added to our community.</p>
                                            <p>Please login to your account with the following details:</p>
                                            <p>Username: <b><i>{ username }</i></b></p>
                                        </div>
                                    </div>
                                </body>
                                </html>
                                """
        
        mail.send(msg)
        
        return redirect(url_for('user.userLogin'))
    else:
        return render_template('addUser.html')






@user_bp.route('/userLogin', methods=['GET'])
def show_login():
    return render_template('userLogin.html')

    
#login
@user_bp.route('/userLogin', methods=['POST'])
def userLogin():
    if request.method == 'POST':
        username = request.form.get('username')  # Assuming your login form has 'username' and 'password' fields
        password = request.form.get('password')
        remember_me = request.form.get('remember_me')
        
        user = User.query.filter_by(Username=username, Password=hashlib.sha256(password.encode()).hexdigest(), RoleId=3).first()
        
        if user:
            session.clear()
            session['user_id'] = user.id
            session['user_role'] = user.RoleId # Storing user ID in the session
            if remember_me:
                session.permanent = True
            else:
                session.permanent = False
                
            print(session.permanent)
            return redirect(url_for('user.index'))  # Redirect to contributor dashboard
        else:
            flash("Login failed. Please try again.", "error")
            return redirect(url_for('user.show_login'))
    else:
        return render_template('UserLogin.html')




@user_bp.route('/view/<int:explanation_id>', methods=['GET', 'POST'])
def view(explanation_id):
    explanation = Explanation.query.get_or_404(explanation_id)
    print(type(explanation))
        
        
    today = datetime.datetime.now().date()
    if today.day == 1:
        explanation.ViewsLastMonth = explanation.ViewsThisMonth
        explanation.ViewsThisMonth = 0

    explanation.Views += 1
    explanation.ViewsToday += 1
    explanation.ViewsThisMonth += 1

    # Check if a new month has started

    db.session.commit()

    return render_template('explanation_view.html', explanation=explanation)




@user_bp.route('/topics')
def topics():
    # Query only explanations where 'approved' is True
    topics = Explanation.query.filter(Explanation.Approved == True).with_entities(Explanation.id, Explanation.Topic).all()
    return render_template('topic_list.html', topics=topics)



#profile
@user_bp.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        abort(403) 
    elif session['user_role'] != 3:
        abort(403) 
        
    user_id = session['user_id']
    user = User.query.get(user_id)
    if user is None:
        abort(404)  # User not found
    
    if request.method == 'POST':
        data = request.form
        # Handle form submission to update user profile
        user.Name = data['name']
        user.Email = data['email']
        user.Username = data['username']
        # Update other profile fields as needed
        db.session.commit()
        return redirect(url_for('user.profile'))
    else:
        return render_template('UserProfile.html', user = user)



@user_bp.route('/changePassword', methods=['GET', 'POST'])
def changePassword():
    if 'user_id' not in session:
        abort(403) 
    elif session['user_role'] != 3:
        abort(403) 

    user_id = session['user_id']
    user = User.query.get(user_id)

    if user is None:
        abort(404)  # User not found

    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        # Check if the current password matches the user's actual password
        if  user.Password == hashlib.sha256(current_password.encode()).hexdigest():
            if new_password == confirm_password:
                user.Password = hashlib.sha256(new_password.encode()).hexdigest()
                db.session.commit()
                return redirect(url_for('user.profile'))
            else:
                flash('New password and confirmation password do not match', 'error')
        else:
            flash('Current password is incorrect', 'error')
            
    return render_template('UserChangePpassword.html', user=user)



@user_bp.route('/logout')
def logout():
    session.clear()
    return redirect('/')
