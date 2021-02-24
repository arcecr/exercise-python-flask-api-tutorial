from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(150), nullable=False)
    done = db.Column(db.Boolean(), default=False)

    def __repr__(self):
        return '<Todo %r>' % self.id

    def serialize(self):
        return {
            "id": self.id,
            "label": self.label,
            "done": self.done
        }