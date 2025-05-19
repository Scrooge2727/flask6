from swagger_server.sqldate import db

class New(db.Model):
    __tablename__ = 'database'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)

    def __init__(self, name, email, id=None):
        self.id = id
        self.name = name
        self.email = email

    @classmethod
    def from_dict(cls, dikt):
        # Если передан словарь, возвращаем объект  Note
        return cls(
            id=dikt.get('id'),
            name=dikt.get('name'),
            email=dikt.get('email')
        )

    def __repr__(self):
        return f'<User {self.name}>'

    def to_dict(self):
        return {"id": self.id, "name": self.name, "email": self.email}
