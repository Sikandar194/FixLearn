from flask import Blueprint, redirect, render_template, request, url_for
from Models.roles_model import db, Role

role_bp = Blueprint("role", __name__, template_folder="templates/roles")



#Add role
@role_bp.route('/add_role', methods=['GET', 'POST'])
def add_role():
    if request.method == 'POST':
        data = request.form
        new_role = Role(name=data['name'], description=data['description'], SeniorityLevel=int(data['SeniorityLevel']))
        db.session.add(new_role)
        db.session.commit()
        return redirect(url_for('role.add_role'))
    else:
        return render_template('add_role.html')


#Update Role
@role_bp.route('/update_role', methods=['GET', 'POST'])
def update_role():
    if request.method == 'POST':
        data = request.form
        role = Role.query.get(data['id'])
        if role:
            role.name = data['name']
            role.description = data['description']
            role.SeniorityLevel = int(data['seniority_level'])
            db.session.commit()
            return redirect(url_for('role.update_role'))
    else:
        roles = Role.query.filter_by(deleted=False).all()
        return render_template('update_role.html', roles=roles)
    

#Delete Role
@role_bp.route('/delete_role', methods=['GET', 'POST'])
def delete_role():
    if request.method == 'POST':
        role_id = int(request.form['role_id'])
        role = Role.query.get(role_id)
        if role:
            role.deleted = True
            db.session.commit()
            return redirect(url_for('role.delete_role'))
    else:
        roles = Role.query.filter_by(deleted=False).all()
        return render_template('delete_role.html', roles=roles)