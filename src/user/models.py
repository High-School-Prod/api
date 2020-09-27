from src import db


class User(db.Model):

    """User model in database"""

    __tablename__ = 'users' # Name of table with users

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), nullable=False, unique=True)
    password = db.Column(db.String(128), nullable=False)
    status = db.Column(db.String(250))
    nickname = db.Column(db.String(50))
    avatar = db.Column(db.String(69))
    email = db.Column(db.String(64), nullable=False, unique=True)

    def __repr__(self):
        return '{}<{}>'.format(self.username, self.id)

    async def validate(self):
        """Validates if there are no conflicts in database"""
        user = await User.query.where(
            (User.username == self.username)
            | (User.email == self.email)
        ).gino.first()

        return False if user else True
