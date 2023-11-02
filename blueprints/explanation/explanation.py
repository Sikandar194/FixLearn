from flask import Blueprint, redirect, render_template, request, session, url_for
from Models.explanation_model import db, Explanation
from datetime import datetime

explanation_bp = Blueprint("explanation_bp", __name__)



#Add role
@explanation_bp.route('/add_explanation', methods=['GET', 'POST'])
def add_explanation():
    
    if request.method == 'POST':
        data = request.form
        new_explanation = Explanation(TopicId=data['TopicId'], Explanation=data['Explanation'], PublishDate=datetime.now)
        db.session.add(new_explanation)
        db.session.commit()
        return redirect(url_for('explanation.add_explanation'))
    else:
        return render_template('add_explanation.html')


#Update Role
@explanation_bp.route('/update_explanation', methods=['GET', 'POST'])
def update_explanation():
    if request.method == 'POST':
        data = request.form
        explanation = Explanation.query.get(data['id'])
        if explanation:
            explanation.TopicId = data['TopicId']
            explanation.Explanation = data['Explanation']
            explanation.EditedOn = datetime.now
            db.session.commit()
            return redirect(url_for('explanation.update_explanation'))
    else:
        explanations = Explanation.query.all()
        return render_template('update_explanation.html', explanation=explanation)
    

#Delete Role
@explanation_bp.route('/delete_explanation', methods=['GET', 'POST'])
def delete_explanation():
    if request.method == 'POST':
        explanation_id = int(request.form['role_id'])
        role = Explanation.query.get(explanation_id)
        if role:
            role.deleted = True
            db.session.commit()
            return redirect(url_for('role.delete_role'))
    else:
        explanations = Explanation.query.filter_by(deleted=False).all()
        return render_template('delete_role.html', explanations=explanations)
    
    
    
    

@explanation_bp.route('/view/<int:explanation_id>', methods=['GET', 'POST'])
def view(explanation_id):
    explanation = Explanation.query.get_or_404(explanation_id)
    print(type(explanation))


    if 'viewed_explanation_' + str(explanation_id) in session:
        #viewed_in_session = True
        return render_template('explanation_view.html', explanation=explanation)
    else:
        #viewed_in_session = False
        # Mark the explanation as viewed in the current session
        session['viewed_explanation_' + str(explanation_id)] = True
        db.session.commit()  # Save the session changes
        
        
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




@explanation_bp.route('/topics')
def topics():
    topics = Explanation.query.with_entities(Explanation.id, Explanation.Topic).all()
    return render_template('topic_list.html', topics=topics)
