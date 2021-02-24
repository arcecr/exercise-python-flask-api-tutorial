import os
from flask_admin import Admin
from models import db, Todo
from flask_admin.contrib.sqla import ModelView

def setup_admin(app):

    app.config['FLASK_ADMIN_SWATCH'] = 'darkly'

    admin = Admin(app, name='Todos App', template_mode='bootstrap3')

    # ModelsView
    admin.add_view(ModelView(Todo, db.session))