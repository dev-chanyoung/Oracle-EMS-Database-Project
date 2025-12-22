from flask import Blueprint, render_template, request, flash, g
import cx_Oracle

sign = Blueprint('sign', __name__)

@sign.route('/templates/sign', methods=['GET', 'POST'])
def employee():
    employees = []
    employee_to_edit = None
    try:
        if request.method == 'POST':
            if 'add_employee' in request.form:
                add_employee()
            elif 'edit_employee' in request.form:
                employee_to_edit = edit_employee()
            elif 'update_employee' in request.form:
                update_employee()
            else:
                flash("Unknown action", 'error')
        else:
            employees = get_all_employees()
    except cx_Oracle.DatabaseError as e:
        flash(f"Database error: {e}", 'error')
    return render_template('sign.html', employees=employees, employee_to_edit=employee_to_edit)

def add_employee():
    cursor = g.db.cursor()
    username = request.form['username']
    
    cursor.execute("""
        SELECT 1 FROM employee WHERE username = :username
    """, {'username': username})
    if cursor.fetchone():
        flash("The username(ID) is already taken. Please choose a different one.", 'error')
        return

    employee_data = (
        request.form['department_id'],
        request.form['employee_name'],
        request.form['registration_number'],
        request.form['education_level'], # 필수 옵션이므로 [] 사용
        request.form.get('skill_set'), # 선택 옵션이므로 get() 사용
        request.form.get('employee_email'),
        request.form.get('employee_phone_number'),
        request.form.get('employee_address'),
        username,   # 아이디 중복 검사를 위해 위에서 먼저 가져옴
        request.form['passwd'],
    )
    cursor.execute("""
        INSERT INTO employee (employee_id, department_id, employee_name, registration_number, education_level, skill_set, employee_email, employee_phone_number, employee_address, username, passwd)
        VALUES (employee_id_seq.NEXTVAL, :1, :2, :3, :4, :5, :6, :7, :8, :9, :10)
    """, employee_data)
    g.db.commit()
    flash(f"Added employee: {employee_data}", 'success')

def edit_employee():
    cursor = g.db.cursor()
    employee_id = request.form['edit_employee_id']
    cursor.execute("""
        SELECT employee_id, employee_name, department_id, registration_number, education_level, skill_set, employee_email, employee_phone_number, employee_address, username, passwd
        FROM employee
        WHERE employee_id = :employee_id
    """, {'employee_id': employee_id})
    employee = cursor.fetchone()
    return employee

def update_employee():
    cursor = g.db.cursor()
    employee_id = request.form.get('employee_id')
    username = request.form['username']

    cursor.execute("""
        SELECT 1 FROM employee WHERE username = :username AND employee_id != :employee_id
    """, {'username': username, 'employee_id': employee_id})
    if cursor.fetchone():
        flash("The username(ID) is already taken by another employee. Please choose a different one.", 'error')
        return

    employee_data = {
        'employee_id': employee_id,
        'employee_name': request.form['employee_name'],
        'department_id': request.form['department_id'],
        'registration_number': request.form['registration_number'],
        'education_level': request.form['education_level'],
        'skill_set': request.form.get('skill_set'),
        'employee_email': request.form.get('employee_email'),
        'employee_phone_number': request.form.get('employee_phone_number'),
        'employee_address': request.form.get('employee_address'),
        'username' : username,
        'passwd' : request.form['passwd'],
    }
    cursor.execute("""
        UPDATE employee
        SET employee_name = :employee_name,
            department_id = :department_id,
            registration_number = :registration_number,
            education_level = :education_level,
            skill_set = :skill_set,
            employee_email = :employee_email,
            employee_phone_number = :employee_phone_number,
            employee_address = :employee_address,
            username = :username,
            passwd = :passwd
        WHERE employee_id = :employee_id
    """, employee_data)
    g.db.commit()
    flash(f"Updated employee: {employee_data['employee_id']}", 'success')

def get_all_employees():
    cursor = g.db.cursor()
    cursor.execute("""
        SELECT employee_id, employee_name, department_name, employee_address, employee_phone_number, employee_email
        FROM employee JOIN department
        ON employee.department_id = department.department_id
        ORDER BY employee_id
    """)
    employees = cursor.fetchall()
    return employees