# app.py
import os
from flask import Flask
from db import init_db


def create_app():
    app = Flask(__name__)
    app.secret_key = os.urandom(24)

    # Initialize the database
    init_db(app)

    
    # Register blueprints
    import main_views
    import test_views
    import sign_views
    import salary_views
    import search_views
    app.register_blueprint(main_views.main)
    app.register_blueprint(test_views.test)
    app.register_blueprint(sign_views.sign)
    app.register_blueprint(salary_views.salary)
    app.register_blueprint(search_views.search_em)
    
    return app

if __name__ == '__main__':
    app = create_app()

    app.run(debug=True, port=5000)