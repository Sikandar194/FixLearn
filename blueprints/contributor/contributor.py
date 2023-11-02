import logging
import bleach
import hashlib
import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from sqlalchemy import desc, func
from Models.category_model import Category
from Models.subject_model import Subject
from .. import mail
from bleach.css_sanitizer import CSSSanitizer
from flask_mail import Message
from Models.user_model import  User, db
from Models.explanation_model import Explanation
from flask import Blueprint, abort, render_template, redirect, request, session, url_for, flash, send_file



contributor_bp = Blueprint("contributor", __name__, template_folder="templates/contributors")
# Access the logger defined in main.py
logger = logging.getLogger(__name__)



@contributor_bp.route('/')
@contributor_bp.route('/contributorIndex')
def contributorIndex():
    
    if 'user_id' not in session:
        return render_template('error-403.html')
    elif session['user_role'] != 2:
        return render_template('error-403.html')
        
        
    contributor_id = session.get('user_id')

    views_today = db.session.query(db.func.sum(Explanation.ViewsToday)).filter(Explanation.ContributorId == contributor_id).scalar() or 0
    Total_views = db.session.query(db.func.sum(Explanation.Views)).filter(Explanation.ContributorId == contributor_id).scalar() or 0
    views_this_month = db.session.query(db.func.sum(Explanation.ViewsThisMonth)).filter(Explanation.ContributorId == contributor_id).scalar() or 0
    views_last_month = db.session.query(db.func.sum(Explanation.ViewsLastMonth)).filter(Explanation.ContributorId == contributor_id).scalar() or 0

    top_explanations = Explanation.query.filter_by(ContributorId=contributor_id).order_by(desc(Explanation.Views)).limit(3).all()
        
    return render_template('contributorIndex.html',
                           views_today=views_today,
                            views_this_month=views_this_month,
                            views_last_month=views_last_month,
                            Total_views=Total_views,
                            top_explanations = top_explanations
                           )



# Route for displaying the login form
@contributor_bp.route('/contributorLogin', methods=['GET'])
def show_login():
    return render_template('contributorLogin.html')


#login
@contributor_bp.route('/contributorLogin', methods=['POST'])
def contributorLogin():
    if request.method == 'POST':
        username = request.form.get('username')  # Assuming your login form has 'username' and 'password' fields
        password = request.form.get('password')
        
        
        user = User.query.filter_by(
            Username=username,
            Password=hashlib.sha256(password.encode()).hexdigest(),
            RoleId=2
            ).first()
        
        if user:
            session.clear()
            session['user_id'] = user.id
            session['user_role'] = user.RoleId
            session['username'] = user.Username
            session['user_email'] = user.Email # Storing user ID in the session
            session.permanent = True
            return redirect(url_for('contributor.contributorIndex'))  # Redirect to contributor dashboard
        
        else:
            flash("Login failed. Please try again.", "error")
            return redirect(url_for('contributor.show_login'))
        
    else:
        return render_template('contributorLogin.html')
    
    
    
    
    
    
    
    
    
    
def generate_pdf(posts):
    # Create a PDF document
    pdf_filename = "posts.pdf"
    doc = SimpleDocTemplate(pdf_filename, pagesize=letter)
    elements = []
    
    # Define the table data
    data = []
    data.append(["Post ID", "Topic","Views", "Date"])
    for post in posts:
        if len(post.Topic) > 20:
            topic= post.Topic[:20-3] + "..."  # Truncate and add "..."
        else:
            topic = post.Topic
            
        data.append([str(post.id), topic,str(post.Views), post.PublishDate.strftime('%d/%m/%Y')])
    
    # Create the table
    table = Table(data, colWidths=[50, 300, 120])
    table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                               ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                               ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                               ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                               ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                               ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                               ('GRID', (0, 0), (-1, -1), 1, colors.black)]))
    elements.append(table)
    
    # Build the PDF document and save it
    doc.build(elements)
    
    return pdf_filename




@contributor_bp.route('/download-pdf')
def download_pdf():
    contributor_id = session['user_id']
    approved_posts = Explanation.query.filter_by(Approved=True, ContributorId=contributor_id).all()
    
    pdf_filename = generate_pdf(approved_posts)
    
    return send_file(pdf_filename, as_attachment=True)   
    
    
    
    
    
    
    
#insert data
@contributor_bp.route('/contributorAddPost', methods=['GET', 'POST'])
def contributorAddPost():
    
    if 'user_id' not in session:
        return render_template('error-403.html')
    elif session['user_role'] != 2:
        return render_template('error-403.html')
        
    if request.method == 'POST':
        
        data = request.form
        
        css_sanitizer = CSSSanitizer(
            allowed_css_properties=["color", "font-weight", "text-align", "background-color", 
                                    "margin", "padding", "hyphens","line-height","margin-right",
                                    "margin-left", "margin-bottom", "margin-top", "display" 
                                    "grid-template-columns", "font-size", "font-family", 
                                    "word-break", "hyphens", "line-height", "padding-right",
                                    "padding-left", "padding-bottom", "padding-top", "border-bottom",
                                    "border-top", "border-left", "border-right"
                                    ]
                                   )
        
        
        tags= ['br','u', 'i','blockquote','h1',  'h2', 'h3', 'h4', 'h5',  'h6', 'font', 'ul','ol',
                    'li', 'p', 'span', 'br',
                    'table', 'tbody', 'tr', 'td',
                    'a', 'img', 'b' ,"span", 'color', 'strong', 'dt', "dd", "dl", "div", "section"
                ]
        attrs = {
                    '*': ['style', 'class', 'href', 'target']
                }

        filterDate = bleach.clean(
            data['explanation'],
            tags= tags,
            attributes=attrs,
            css_sanitizer=css_sanitizer
            ) # remove threat of <script></script>
        
        new_explanation = Explanation(
            Topic=data['topic'], 
            Explanation=filterDate, 
            PublishDate=datetime.datetime.now(), 
            ContributorId = session['user_id'], 
            CategoryId = int(data['categoryid']), 
            SubjectId = int(data['subjectid'])
            )
        
        db.session.add(new_explanation)
        db.session.commit()
        
        user_id = session['user_id']
        username = User.query.filter_by(id=user_id, RoleId=2).first().Username
        useremail = User.query.filter_by(id=user_id).first().Email
        email = []
        
        email = tuple([useremail, "bizintro1@gmail.com"])
        
     
        # subject = "Post added !"
        # html_body = f"""<!DOCTYPE html>
        #                         <html>
        #                         <head>
        #                             <meta charset="UTF-8">
        #                             <title>New Post</title>
        #                             <style>
        #                                 body {{
        #                                     font-family: Arial, sans-serif;
        #                                     background-color: #f7f7f7;
        #                                     margin: 0;
        #                                     padding: 0;
        #                                 }}
        #                                 .container {{
        #                                     max-width: 600px;
        #                                     margin: 0 auto;
        #                                     padding: 20px;
        #                                     background-color: #fff;
        #                                     border-radius: 10px;
        #                                     box-shadow: 0px 2px 5px rgba(0, 0, 0, 0.1);
        #                                 }}
        #                                 .header {{
        #                                     background-color: #007bff;
        #                                     color: #fff;
        #                                     text-align: center;
        #                                     padding: 10px;
        #                                     border-top-left-radius: 10px;
        #                                     border-top-right-radius: 10px;
        #                                 }}
        #                                 .message {{
        #                                     padding: 20px;
        #                                 }}
        #                             </style>
        #                         </head>
        #                         <body>
        #                             <div class="container">
        #                                 <div class="header">
        #                                     <h1>New Post Pending Approval</h1>
        #                                 </div>
        #                                 <div class="message">
        #                                     <p>Hi <b>{ username }</b>,</p>
        #                                     <p>Your new post has been added to the pending list and is waiting for approval from the admin.</p>
        #                                     <p>Once your post is approved, it will be published on the website.</p>
        #                                     <p>Thank you for your contribution!</p>
        #                                     <p>Domain</p>
        #                                 </div>
        #                             </div>
        #                         </body>
        #                         </html>
        #                         """
        # recipients  = [useremail, "bizintro1@gmail.com"]
        # print(recipients)
        # send_email.apply_async(args=[subject, "bizintro1@gmail.com", recipients, html_body])
        # print("post function... email sent...")
        
        msg = Message("Post added !",
                      sender = "bizintro1@gmail.com",
                  recipients=[email])
        
        
        
        msg.html = f"""<!DOCTYPE html>
                                <html>
                                <head>
                                    <meta charset="UTF-8">
                                    <title>Adding Post</title>
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
                                            <h1>New Post Pending Approvaly</h1>
                                        </div>
                                        <div class="message">
                                            <p>Hi <b>{ username }</b>,</p>
                                            <p>Your new post has been added to the pending list and is waiting for approval from the admin.</p>
                                            <p>Once your post is approved, it will be published on the website.</p>
                                            <p>Thank you for your contribution!</p>
                                        </div>
                                    </div>
                                </body>
                                </html>
                                """
        
        mail.send(msg)
        # cache.clear()
        return redirect(url_for('contributor.contributorAddPost'))
    else:
        categories = Category.query.all()
        subjects = Subject.query.all()
        return render_template('contributorAddPost.html', categories=categories, subjects = subjects)




# @cache.cached(timeout=3600) 
@contributor_bp.route('/topics')
def topics():
    
    if 'user_id' not in session:
        return render_template('error-403.html')
    elif session['user_role'] != 2:
        return render_template('error-403.html')
        
    topics = Explanation.query.with_entities(
                                    Explanation.id, Explanation.Topic
                                    ).filter_by(
                                        ContributorId=session['user_id']
                                            ).all()
                                    
    return render_template('topic_list_contributor.html', topics=topics)




@contributor_bp.route('/contributorViewPost/<int:explanation_id>', methods=['GET', 'POST'])
def contributorViewPost(explanation_id):
    if 'user_id' not in session:
        return render_template('error-403.html')
    elif session['user_role'] != 2:
        return render_template('error-403.html') 
        
    explanation = Explanation.query.get_or_404(explanation_id)

    return render_template('contributorViewPost.html', explanation=explanation)




#edit post
@contributor_bp.route('/contributorEditPost/<int:explanation_id>', methods=['GET', 'POST'])
def contributorEditPost(explanation_id):
    explanation = Explanation.query.get(explanation_id)
    
    if  explanation == None:
        return render_template('error-404.html')
    
    if 'user_id' not in session:
        return render_template('error-403.html')
    elif session['user_role'] != 2:
        return render_template('error-403.html')
    
    if explanation.ContributorId != session['user_id']:
        print("You are not the owner of this explanation ")
        abort(403)
        
   
    
    
    if request.method == 'POST':
        data = request.form
        explanation.Topic = data['Topic']
        explanation.Explanation = data['Explanation']
        explanation.EditedOn = datetime.datetime.now()
        
        db.session.commit()
        
        return redirect(url_for('contributor.contributorEditPost', explanation_id=explanation_id))
    else:
        return render_template('editpost.html', explanation=explanation)
    
    

#profile
@contributor_bp.route('/contributorProfile', methods=['GET', 'POST'])
def contributorProfile():
    if 'user_id' not in session:
        abort(403) 
    elif session['user_role'] != 2:
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
        return redirect(url_for('contributor.contributorProfile'))
    else:
        return render_template('contributorProfile.html', user = user)



@contributor_bp.route('/contributorChangePassword', methods=['GET', 'POST'])
def contributorChangePassword():
    if 'user_id' not in session:
        abort(403) 
    elif session['user_role'] != 2:
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
                return redirect(url_for('contributor.contributorProfile'))
            else:
                flash('New password and confirmation password do not match', 'error')
        else:
            flash('Current password is incorrect', 'error')
            
    return render_template('contributorChangePassword.html', user=user)




@contributor_bp.route('/contributorPosts')
def contributorPosts():
    if 'user_id' not in session:
        return render_template('error-403.html')
    elif session['user_role'] != 2:
        return render_template('error-403.html')
    contributor_id = session['user_id']
    
    pending_posts = Explanation.query.filter_by(
        Pending=True, 
        ContributorId = contributor_id
        ).order_by(desc(Explanation.PublishDate)).all()
    
    rejected_posts = Explanation.query.filter_by(
        Deleted=True,
        ContributorId = contributor_id
        ).order_by(desc(Explanation.PublishDate)).all()
    
    
    total_views = db.session.query(
        func.sum(Explanation.Views)
        ).filter_by(
            ContributorId = contributor_id
            ).scalar()
    
    
    approved_posts = Explanation.query.filter_by(
        Approved=True,
        ContributorId = contributor_id
        ).order_by(desc(Explanation.PublishDate)).all()
    
    return render_template('contributorPosts.html',
                           pending_posts=pending_posts,
                           rejected_posts=rejected_posts,
                           approved_posts =approved_posts,
                           total_views = total_views
                           )



@contributor_bp.route('/contributorRejectedPosts')
def contributorRejectedPosts():
    if 'user_id' not in session:
        return render_template('error-403.html')
    elif session['user_role'] != 2:
        return render_template('error-403.html')

    rejected_posts = Explanation.query.filter_by(Deleted=True).all()
    return render_template('contributorRejectedPosts.html', rejected_posts=rejected_posts)




@contributor_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('contributor.contributorLogin'))