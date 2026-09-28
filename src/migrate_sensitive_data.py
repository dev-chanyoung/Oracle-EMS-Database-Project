# migrate_sensitive_data.py
# 이미 평문으로 저장된 비밀번호·주민등록번호를 해시/암호문으로 바꾼다.
# 바뀐 행은 건너뛰므로 여러 번 실행해도 된다.
#   python migrate_sensitive_data.py
from db import connect, init_oracle_client
from security import encrypt_rrn, hash_password, is_password_hash, is_plain_rrn

RRN_COLUMN_LENGTH = 100


def widen_rrn_column(cursor):
    # 암호문(base64)은 평문 14자보다 길어서 컬럼부터 넓힌다
    cursor.execute("""
        SELECT data_length FROM user_tab_columns
        WHERE table_name = 'EMPLOYEE' AND column_name = 'REGISTRATION_NUMBER'
    """)
    (length,) = cursor.fetchone()
    if length < RRN_COLUMN_LENGTH:
        cursor.execute(f"ALTER TABLE employee MODIFY registration_number VARCHAR2({RRN_COLUMN_LENGTH})")


def migrate(conn):
    cursor = conn.cursor()
    widen_rrn_column(cursor)
    cursor.execute("SELECT employee_id, registration_number, passwd FROM employee")
    updates = []
    for employee_id, rrn, passwd in cursor.fetchall():
        new_rrn = encrypt_rrn(rrn) if is_plain_rrn(rrn) else rrn
        new_passwd = passwd if is_password_hash(passwd) else hash_password(passwd)
        if (new_rrn, new_passwd) != (rrn, passwd):
            updates.append({'employee_id': employee_id, 'rrn': new_rrn, 'passwd': new_passwd})
    if updates:
        cursor.executemany("""
            UPDATE employee
            SET registration_number = :rrn, passwd = :passwd
            WHERE employee_id = :employee_id
        """, updates)
    conn.commit()
    return len(updates)


if __name__ == '__main__':
    init_oracle_client()
    with connect() as conn:
        print(f"Converted {migrate(conn)} employee rows")
