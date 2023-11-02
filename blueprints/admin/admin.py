# Import statements should be at the top of the file.
import secrets
import string
import random
import hashlib
import logging
from flask import (
    Blueprint,
    render_template,
    redirect,
    request,
    session,
    url_for,
    flash,
    abort,
    jsonify,
)
from flask_mail import Message
from sqlalchemy import func
from Models.category_model import Category
from Models.roles_model import Role
from Models.subject_model import Subject
from Models.user_model import User, db
from Models.explanation_model import Explanation
from .. import mail

# Define the admin blueprint.
admin_bp = Blueprint("admin", __name__, template_folder="templates/admin")

# Access the logger defined in main.py
logger = logging.getLogger(__name__)


# Dashboard
@admin_bp.route('/adminIndex')
@admin_bp.route('/')
def adminIndex():
    if 'user_id' not in session:
        return render_template('error-403.html')
    elif session['user_role'] != 1:
        return render_template('error-403.html')

    # Calculate various statistics
    views_today = db.session.query(db.func.sum(Explanation.ViewsToday)).scalar() or 0
    Total_views = db.session.query(db.func.sum(Explanation.Views)).scalar() or 0
    views_this_month = db.session.query(db.func.sum(Explanation.ViewsThisMonth)).scalar() or 0
    views_last_month = db.session.query(db.func.sum(Explanation.ViewsLastMonth)).scalar() or 0

    # Contributor Views
    contributor_views = db.session.query(
        User.Name, func.sum(Explanation.Views).label("TotalViews")
    ).join(
        Explanation, User.id == Explanation.ContributorId
    ).group_by(
        User.Name
    ).all()

    # Top Subjects
    views_sum = func.sum(Explanation.Views).label("total_views")
    subject_views_query = (
        db.session.query(Subject.id, Subject.Name, views_sum)
        .join(Explanation, Explanation.SubjectId == Subject.id)
        .group_by(Subject.id, Subject.Name)
        .order_by(views_sum.desc())
        .all()
    )

    # Top Category
    category_views_query = (
        db.session.query(Category.Name, views_sum)
        .join(Explanation, Explanation.CategoryId == Category.Id)
        .group_by(Category.Name)
        .order_by(views_sum.desc())
        .first()
    )

    top_category = None

    if category_views_query:
        highest_views_category_name, total_views = category_views_query
        top_category = highest_views_category_name, total_views

    return render_template(
        'adminIndex.html',
        views_today=views_today,
        views_this_month=views_this_month,
        views_last_month=views_last_month,
        Total_views=Total_views,
        contributor_views=contributor_views,
        subject_views_query=subject_views_query,
        top_category=category_views_query,
    )


# API endpoint to get chart data
@admin_bp.route('/api/get_chart_data', methods=['GET'])
def get_chart_data():
    contributor_view = db.session.query(
        User.Name, func.sum(Explanation.Views).label("TotalViews")
    ).join(
        Explanation, User.id == Explanation.ContributorId
    ).group_by(
        User.Name
    ).all()

    contributor_data = []
    for row in contributor_view:
        dictionary = {
            "Name": row[0],
            "TotalViews": row[1],
        }
        contributor_data.append(dictionary)
    return jsonify(contributor_data)


# Add Admin
@admin_bp.route('/adminRegister', methods=['GET', 'POST'])
def adminRegister():
    if request.method == 'POST':
        # Only admin can add new Admin
        if 'user_id' not in session:
            return render_template('error-403.html')
        elif session['user_role'] != 1:
            return render_template('error-403.html')

        # Get data from form
        name = request.form.get('name')
        username = request.form.get('username')
        email = request.form.get('email')

        # Generate a random password
        characters = string.ascii_letters + string.digits + "!@#$%^&*()_-+"
        password = ''.join(random.choice(characters) for _ in range(8))

        # Check whether username already exists or not
        user = User.query.filter_by(Username=username).first()
        if user:
            flash("Username already exists.", "error")
            return redirect(url_for('admin.adminRegister'))

        # Create a new admin user
        new_user = User(
            Name=name,
            Username=username,
            Password=hashlib.sha256(password.encode()).hexdigest(),
            Email=email,
            RoleId=1
        )

        db.session.add(new_user)
        db.session.commit()

        # Send an email to the new admin with their credentials
        msg = Message("Welcome to the Management Team!",
                      sender="bizintro1@gmail.com",
                      recipients=[email])
        msg.html = f"Hi {name},<br>You have been added as an Admin to our community.<br>Please login to your account using the following credentials:<br>Username: {username}<br>Password: {password}"

        mail.send(msg)

        return redirect(url_for('admin.adminIndex'))
    else:
        return render_template('adminRegister.html')


# Login routes


# Route for displaying the login form
@admin_bp.route('/adminLogin', methods=['GET'])
def show_login():
    return render_template('AdminLogin.html')


# Login
@admin_bp.route('/adminLogin', methods=['POST'])
def adminLogin():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember_me = request.form.get('remember_me')

        user = User.query.filter_by(
            Username=username,
            Password=hashlib.sha256(password.encode()).hexdigest(),
            RoleId=1
        ).first()

        if user:
            session.clear()
            session['user_id'] = user.id
            session['user_role'] = user.RoleId
            session['username'] = user.Username

            if remember_me:
                session.permanent = True
            else:
                session.permanent = False

            return redirect(url_for('admin.adminIndex'))
        else:
            flash("Login failed. Please try again.")
            return redirect(url_for('admin.show_login'))
    else:
        return render_template('adminLogin.html')


# Contributors List
@admin_bp.route('/adminContributorslist')
def adminContributorslist():
    if 'user_id' not in session:
        return render_template('error-403.html')
    elif session['user_role'] != 1:
        return render_template('error-403.html')

    contributors = User.query.filter_by(RoleId=2, Deleted=False).all()
    contributors_info = []
    total_views_all_contributors = 0

    for contributor in contributors:
        total_views = db.session.query(func.sum(Explanation.Views)).filter_by(ContributorId=contributor.id).scalar()
        explanation_count = db.session.query(func.count(Explanation.id)).filter_by(ContributorId=contributor.id).scalar()

        if total_views is not None:
            total_views_all_contributors += total_views
        contributors_info.append({'contributor': contributor, 'total_views': total_views, 'explanation_count': explanation_count})

    contributors_info = sorted(contributors_info, key=lambda x: (x['total_views'] or 0), reverse=True)
    return render_template('adminContributorslist.html', contributors_info=contributors_info, total_views_all_contributors=total_views_all_contributors)


@admin_bp.route('/adminDeleteContributor', methods=['GET', 'POST'])
def adminDeleteContributor():
    if 'user_id' not in session:
        return render_template('error-403.html')
    elif session['user_role'] != 1:
        return render_template('error-403.html')

    if request.method == 'POST':
        contributor_id = int(request.form['contributor_id'])
        DelContributor = User.query.get(contributor_id)
        if DelContributor:
            DelContributor.Deleted = True
            db.session.commit()
            return redirect(url_for('admin.adminContributorslist'))
    else:
        Contributors = User.query.filter_by(Deleted=False, RoleId=2).all()
        return redirect(url_for('admin.adminContributorslist'))


# Contributors List
@admin_bp.route('/adminDeletedContributorslist')
def adminDeletedContributorslist():
    if 'user_id' not in session:
        return render_template('error-403.html')
    elif session['user_role'] != 1:
        return render_template('error-403.html')

    contributors = User.query.filter_by(RoleId=2, Deleted=True).all()
    return render_template('adminDeletedContributorslist.html', contributors=contributors)


@admin_bp.route('/adminRecoverContributor', methods=['GET', 'POST'])
def adminRecoverContributor():
    if 'user_id' not in session:
        return render_template('error-403.html')
    elif session['user_role'] != 1:
        return render_template('error-403.html')

    if request.method == 'POST':
        contributor_id = int(request.form['contributor_id'])
        DelContributor = User.query.get(contributor_id)
        if DelContributor:
            DelContributor.Deleted = False
            db.session.commit()
            return redirect(url_for('admin.adminDeletedContributorslist'))
    else:
        Contributors = User.query.filter_by(Deleted=False, RoleId=2).all()
        return redirect(url_for('admin.adminDeletedContributorslist'))


@admin_bp.route('/adminRegisterContributor', methods=['GET', 'POST'])
def adminRegisterContributor():
    if 'user_id' not in session:
        return render_template('error-403.html')
    elif session['user_role'] != 1:
        return render_template('error-403.html')

    if request.method == 'POST':
        name = request.form.get('name')
        username = request.form.get('username')
        email = request.form.get('email')

        characters = string.ascii_lowercase + string.ascii_uppercase + string.digits + "!@#$%^&*()_-+"
        password = ''.join(random.choice(characters) for _ in range(8))

        user = User.query.filter_by(Username=username).first()

        if user:
            flash("Username already exists.", "error")
            return redirect(url_for('admin.adminRegisterContributor'))

        new_user = User(
            Name=name,
            Username=username,
            Password=hashlib.sha256(password.encode()).hexdigest(),
            Email=email,
            RoleId=2
        )

        db.session.add(new_user)
        db.session.commit()

        msg = Message("Welcome to the Contributor Community!",
                      sender="bizintro1@gmail.com",
                      recipients=[email])
        msg.html = f"Hi {name},<br>You have been added as a contributor to our community.<br>Please login to your account using the following credentials:<br>Username: {username}<br>Password: {password}"

        mail.send(msg)

        return redirect(url_for('admin.adminIndex'))
    else:
        return render_template('adminRegisterContributor.html')


@admin_bp.route('/adminContributorTopics')
def adminContributorTopics():
    if 'user_id' not in session:
        return render_template('error-403.html')
    elif session['user_role'] != 1:
        return render_template('error-403.html')

    contributor_id = request.args.get('contributor_id')
    contributor = User.query.get(contributor_id)
    explanations = Explanation.query.filter_by(ContributorId=contributor_id).all()
    return render_template('adminContributorTopics.html', explanations=explanations, contributor=contributor)


@admin_bp.route('/adminViewContributorProfile', methods=['GET', 'POST'])
def adminViewContributorProfile():
    if 'user_id' not in session:
        return render_template('error-403.html')
    elif session['user_role'] != 1:
        return render_template('error-403.html')

    contributor_id = int(request.form['contributor_id'])
    user = User.query.get(contributor_id)
    roles = Role.query.filter_by(Deleted=False).all()

    if user is None:
        abort(404)

    return render_template('adminViewContributorProfile.html', user=user, roles=roles)


@admin_bp.route('/adminContributorProfile', methods=['GET', 'POST'])
def adminContributorProfile():
    if 'user_id' not in session:
        return render_template('error-403.html')
    elif session['user_role'] != 1:
        return render_template('error-403.html')

    contributor_id = request.args.get('contributor_id', default=-1)
    if contributor_id != -1:
        contributor_id = int(contributor_id)
    user = User.query.get(contributor_id)
    
    if user is None:
        abort(404)

    if request.method == 'POST':
        data = request.form
        user.Name = data['name']
        user.Email = data['email']
        user.Username = data['username']
        user.RoleId = data['role']
        db.session.commit()
        return redirect(url_for('admin.adminContributorslist'))
    else:
        return render_template('ViewContributorprofile.html', user=user)


@admin_bp.route('/adminAprovedPosts')
def adminAprovedPosts():
    if 'user_id' not in session:
        return render_template('error-403.html')
    elif session['user_role'] != 1:
        return render_template('error-403.html')

    topics = Explanation.query.filter_by(Pending=False, Deleted=False, Approved=True).with_entities(
        Explanation.id, Explanation.Topic, Explanation.Views).all()
    return render_template('adminAprovedPosts.html', topics=topics)


@admin_bp.route('/adminPostView/<int:explanation_id>', methods=['GET', 'POST'])
def adminPostView(explanation_id):
    if 'user_id' not in session:
        return render_template('error-403.html')
    elif session['user_role'] != 1:
        return render_template('error-403.html')

    explanation = Explanation.query.get_or_404(explanation_id)
    return render_template('adminPostView.html', explanation=explanation)


@admin_bp.route('/adminPendingPosts')
def adminPendingPosts():
    if 'user_id' not in session:
        return render_template('error-403.html')
    elif session['user_role'] != 1:
        return render_template('error-403.html')

    pending_posts = Explanation.query.filter_by(Pending=True).all()
    return render_template('adminPendingPosts.html', pending_posts=pending_posts)



@admin_bp.route('/adminRejectedPosts')
def adminRejectedPosts():
    if 'user_id' not in session:
        return render_template('error-403.html')
    elif session['user_role'] != 1:
        return render_template('error-403.html')

    rejected_posts = Explanation.query.filter_by(Deleted=True).all()
    return render_template('adminRejectedPosts.html', rejected_posts=rejected_posts)


@admin_bp.route('/adminApprovePost/<int:post_id>', methods=['POST'])
def adminApprovePost(post_id):
    if 'user_id' not in session:
        return render_template('error-403.html')
    elif session['user_role'] != 1:
        return render_template('error-403.html')

    post = Explanation.query.get_or_404(post_id)
    post.Pending = False
    post.Approved = True
    db.session.commit()
    contributor_id = post.ContributorId
    useremail = User.query.filter_by(id=contributor_id).first().Email
    username = User.query.filter_by(id=contributor_id).first().Username

    msg = Message("Post Approved !",
                  sender="bizintro1@gmail.com",
                  recipients=[useremail])

    msg.html = f"""<!DOCTYPE html>
                            <html>
                            <head>
                                <meta charset="UTF-8">
                                <title>Post Approved</title>
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
                                        <h1>Post Approval</h1>
                                    </div>
                                    <div class="message">
                                        <p>Hi <b>{ username }</b>,</p>
                                        <p>Your post: {post.Topic} \n has been approved by the team.</p>
                                        <p>Now it is published on our website.</p>
                                        <p>Thank you for your contribution!</p>
                                    </div>
                                </div>
                            </body>
                            </html>
                            """

    mail.send(msg)
    return redirect(url_for('admin.adminPendingPosts'))


@admin_bp.route('/adminRejectPost/<int:post_id>', methods=['POST'])
def adminRejectPost(post_id):
    if 'user_id' not in session:
        return render_template('error-403.html')
    elif session['user_role'] != 1:
        return render_template('error-403.html')

    post = Explanation.query.get_or_404(post_id)
    post.Pending = False
    post.Approved = False
    post.Deleted = True
    db.session.commit()
    return redirect(url_for('admin.adminPendingPosts'))


@admin_bp.route('/adminProfile', methods=['GET', 'POST'])
def adminProfile():
    if 'user_id' not in session:
        return render_template('error-403.html')
    elif session['user_role'] != 1:
        return render_template('error-403.html')

    user_id = session['user_id']
    user = User.query.get(user_id)
    if user is None:
        return render_template('error-404.html')

    if request.method == 'POST':
        data = request.form
        user.Name = data['name']
        user.Email = data['email']
        user.Username = data['username']
        db.session.commit()
        return redirect(url_for('admin.adminProfile'))
    else:
        return render_template('adminProfile.html', user=user)


@admin_bp.route('/adminChangePassword', methods=['GET', 'POST'])
def adminChangePassword():
    if 'user_id' not in session:
        return render_template('error-403.html')
    elif session['user_role'] != 1:
        return render_template('error-403.html')

    user_id = session['user_id']
    user = User.query.get(user_id)

    if user is None:
        return render_template('error-404.html')

    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if user.Password == hashlib.sha256(current_password.encode()).hexdigest():
            if new_password == confirm_password:
                user.Password = hashlib.sha256(new_password.encode()).hexdigest()
                db.session.commit()
                return redirect(url_for('admin.adminProfile'))
            else:
                flash('New password and confirmation password do not match', 'error')
        else:
            flash('Current password is incorrect', 'error')

    return render_template('adminChangePassword.html', user=user)


@admin_bp.route('/logout')
def logout():
    session.clear()
    return render_template('AdminLogin.html')
