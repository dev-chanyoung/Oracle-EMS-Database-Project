from flask import Blueprint, render_template, request, flash, g
import cx_Oracle

salary = Blueprint('salary', __name__)

# @salary.route('/test/employee', methods=['GET', 'POST'])
# def employee():
#     employees = []
#     employee_to_edit = None
#     try:
#         if request.method == 'POST':
#             if 'add_employee' in request.form:
#                 add_employee()
#             elif 'search_employee' in request.form:
#                 employees = search_employee()
#             elif 'edit_employee' in request.form:
#                 employee_to_edit = edit_employee()
#             elif 'update_employee' in request.form:
#                 update_employee()
#             elif 'delete_employee' in request.form:
#                 delete_employee()
#             else:
#                 flash("Unknown action", 'error')
#         else:
#             employees = get_all_employees()
#     except cx_Oracle.DatabaseError as e:
#         flash(f"Database error: {e}", 'error')
#     return render_template('test/employee.html', employees=employees, employee_to_edit=employee_to_edit)


@salary.route('/salary', methods=['GET', 'POST'])
def employee():
    employees = []
    employee_to_edit = None
    try:
        if request.method == 'POST':
            if 'search_employee' in request.form:
                employees = search_employee()
            else:
                flash("Unknown action", 'error')
        else:
            employees = join_employee_salary()
    except cx_Oracle.DatabaseError as e:
        flash(f"Database error: {e}", 'error')
    return render_template('salary.html', employees=employees, employee_to_edit=employee_to_edit)

def search_employee():
    cursor = g.db.cursor()
    search_id = request.form['search_id'].strip()
    cursor.execute("""
        SELECT e.employee_id, e.employee_name, s.salary_id, s.contract_id, s.monthly_salary
        FROM employee e JOIN salary s ON e.employee_id = s.employee_id
        WHERE e.employee_id = :search_id
        ORDER BY e.employee_id
    """, {'search_id': search_id})  # 정확히 일치하는 ID를 찾기 위해 '=' 사용
    employees = cursor.fetchall()
    flash(f"Found employee with ID '{search_id}'", 'success')
    return employees

def join_employee_salary():
    cursor = g.db.cursor()
    cursor.execute("""
        SELECT employee_id, employee_name, salary_id, contract_id, monthly_salary
        FROM employee JOIN salary
        ON employee.employee_id = salary.employee_id
        ORDER BY employee_id
    """)
    employees = cursor.fetchall()
    return employees