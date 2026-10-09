# migrate_sensitive_data.py
# 이미 평문으로 저장된 비밀번호·주민등록번호를 해시/암호문으로 바꾼다.
# 바뀐 행은 건너뛰므로 여러 번 실행해도 된다.
#
# 사용 순서 (시드 SQL은 평문이라, 적재 "후"에 이 스크립트를 실행해야 한다):
#   1) sql/01_ddl_schema.sql, sql/02_dml_seed_data.sql 을 DB에 적재한다.
#   2) 환경변수를 설정한다: ORACLE_USER, ORACLE_PASSWORD, (ORACLE_DSN), RRN_ENCRYPTION_KEY
#      키 생성: python -c "import os, base64; print(base64.b64encode(os.urandom(32)).decode())"
#   3) src 폴더에서 실행한다:  python migrate_sensitive_data.py
# 실행하기 전에는 시드 직원의 수정 화면(정보 가져오기)이 열리지 않는다 (평문 주민번호는 복호화할 수 없음).
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
