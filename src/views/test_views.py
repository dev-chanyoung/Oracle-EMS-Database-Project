from flask import Blueprint, render_template, request, flash, g
import cx_Oracle

test = Blueprint('test', __name__)

@test.route('/test/department')
def department():
    departments = []
    try:
        cursor = g.db.cursor()
        cursor.execute("SELECT department_id, department_name FROM department")
        departments = cursor.fetchall()
    except cx_Oracle.DatabaseError as e:
        flash(f"Database error: {e}", 'error')
    return render_template('test/department.html', departments=departments)

@test.route('/test/employee', methods=['GET', 'POST'])
def employee():
    employees = []
    employee_to_edit = None
    try:
        if request.method == 'POST':
            if 'add_employee' in request.form:
                add_employee()
            elif 'search_employee' in request.form:
                employees = search_employee()
            elif 'edit_employee' in request.form:
                employee_to_edit = edit_employee()
            elif 'update_employee' in request.form:
                update_employee()
            elif 'delete_employee' in request.form:
                delete_employee()
            else:
                flash("Unknown action", 'error')
        else:
            employees = get_all_employees()
    except cx_Oracle.DatabaseError as e:
        flash(f"Database error: {e}", 'error')
    return render_template('test/employee.html', employees=employees, employee_to_edit=employee_to_edit)

def add_employee():
    cursor = g.db.cursor()
    employee_data = (
        request.form['employee_id'],
        request.form['department_id'],
        request.form['employee_name'],
        request.form['registration_number'],
        request.form['education_level'], # 필수 옵션이므로 [] 사용
        request.form.get('skill_set'), # 선택 옵션이므로 get() 사용
        request.form.get('employee_email'),
        request.form.get('employee_phone_number'),
        request.form.get('employee_address')
    )
    cursor.execute("""
        INSERT INTO employee (employee_id, department_id, employee_name, registration_number, education_level, skill_set, employee_email, employee_phone_number, employee_address)
        VALUES (:1, :2, :3, :4, :5, :6, :7, :8, :9)
    """, employee_data)
    g.db.commit()
    flash(f"Added employee: {employee_data}", 'success')

def search_employee():
    cursor = g.db.cursor()
    search_name = request.form['search_name'].strip()
    cursor.execute("""
        SELECT employee_id, employee_name, department_name, employee_address, employee_phone_number, employee_email
        FROM employee JOIN department
        ON employee.department_id = department.department_id
        WHERE employee_name LIKE :search_name
        ORDER BY employee_id
    """, {'search_name': f'%{search_name}%'})
    employees = cursor.fetchall()
    flash(f"Found employees matching '{search_name}'", 'success')
    return employees

def edit_employee():
    cursor = g.db.cursor()
    employee_id = request.form['edit_employee_id']
    cursor.execute("""
        SELECT employee_id, employee_name, department_id, registration_number, education_level, skill_set, employee_email, employee_phone_number, employee_address
        FROM employee
        WHERE employee_id = :employee_id
    """, {'employee_id': employee_id})
    employee = cursor.fetchone()
    return employee

def update_employee():
    cursor = g.db.cursor()
    employee_data = {
        'employee_id': request.form['employee_id'],
        'employee_name': request.form['employee_name'],
        'department_id': request.form['department_id'],
        'registration_number': request.form['registration_number'],
        'education_level': request.form['education_level'],
        'skill_set': request.form.get('skill_set'),
        'employee_email': request.form.get('employee_email'),
        'employee_phone_number': request.form.get('employee_phone_number'),
        'employee_address': request.form.get('employee_address'),
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
            employee_address = :employee_address
        WHERE employee_id = :employee_id
    """, employee_data)
    g.db.commit()
    flash(f"Updated employee: {employee_data['employee_id']}", 'success')

def delete_employee():
    cursor = g.db.cursor()
    employee_id = request.form['employee_id']
    cursor.execute("DELETE FROM employee WHERE employee_id = :employee_id", {'employee_id': employee_id})
    g.db.commit()
    flash(f"Deleted employee: {employee_id}", 'success')

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