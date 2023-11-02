from flask import Blueprint, redirect, render_template, request, url_for
from Models.resources_model import db, Resource

resource_bp = Blueprint("resource", __name__)


#Add role
@resource_bp.route('/add_resource', methods=['GET', 'POST'])
def add_resource():
    if request.method == 'POST':
        data = request.form
        new_resource = Resource(Name=data['name'], ResourcePath=data['ResourcePath'], TopicId=int(data['TopicId'], SubjectId = int(data['SubjectId']), ExplanationId = int(data['ExplanationId']), Downloads = int(data['Downloads'])))
        db.session.add(new_resource)
        db.session.commit()
        return redirect(url_for('role.add_resource'))
    else:
        return render_template('add_resource.html')


#Update Role
@resource_bp.route('/update_resource', methods=['GET', 'POST'])
def update_resource():
    if request.method == 'POST':
        data = request.form
        new_resource = Resource.query.get(data['id'])
        if new_resource:
            new_resource.name = data['name']
            new_resource.ResourcePath = data['ResourcePath']
            new_resource.TopicId = int(data['TopicId'])
            new_resource.SubjectId = int(data['SubjectId'])
            new_resource.ExplanationId = int(data['ExplanationId'])
            new_resource.Downloads = int(data['Downloads'])
            db.session.commit()
            return redirect(url_for('resource.update_resource'))
    else:
        resources = Resource.query.all()
        return render_template('update_resource.html', roles=resources)
    

#Delete Role
@resource_bp.route('/delete_resource', methods=['GET', 'POST'])
def delete_resource():
    if request.method == 'POST':
        del_resource = int(request.form['resource_id'])
        del_resource_admin = Resource.query.get(del_resource)
        if del_resource_admin:
            del_resource_admin.deleted = True
            db.session.commit()
            return redirect(url_for('resource.delete_resource'))
    else:
        del_resource = Resource.query.filter_by(deleted=False).all()
        return render_template('delete_resource.html', roles=del_resource)
    
    
