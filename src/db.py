# db.py
import os
import platform
import cx_Oracle
from flask import g

def init_db(app):
    # Oracle 클라이언트 초기화
    if os.name == "nt":
        lib_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'instantclient_23_6')
    elif os.name == "posix":
        if platform.system() == "Linux":
            lib_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'instantclient_23_6')
        elif platform.system() == "Darwin":
            lib_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'instantclient_23_3')
    cx_Oracle.init_oracle_client(lib_dir=lib_dir)

    @app.before_request
    def create_db_connection():
        # 접속 정보는 환경변수로 주입
        g.db = cx_Oracle.connect(
            user=os.environ["ORACLE_USER"],
            password=os.environ["ORACLE_PASSWORD"],
            dsn=os.environ.get("ORACLE_DSN", "localhost/XE"),
        )

    @app.teardown_request
    def close_db_connection(exception):
        db = g.pop('db', None)
        if db is not None:
            db.close()