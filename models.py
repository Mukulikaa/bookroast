from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class books(db.Model):
    __tablename__= 'books'
    id = db.Column(db.Integer, primary_key=True)
    title= db.Column(db.String, nullable=False)
    author= db.Column(db.String, nullable=False)
    pub_year= db.Column(db.Integer, nullable=False)
    ISBN= db.Column(db.String, nullable=False)
    ratings = db.Column(db.Float, nullable=True)

class users(db.Model):
    __tablename__= 'users'
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String, nullable=False)
    lname = db.Column(db.String, nullable=False)
    username = db.Column(db.String,unique=True, nullable=False)
    password = db.Column(db.String, unique=True, nullable=False)
    authenticated = db.Column(db.Boolean, default=False)
    def is_active(self):
        """True, as all users are active."""
        return True

    def get_id(self):
        """Return the email address to satisfy Flask-Login's requirements."""
        return self.id

    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return self.authenticated

    def is_anonymous(self):
        """False, as anonymous users aren't supported."""
        return False
        
class reviews(db.Model):
    __tablename__= 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, db.ForeignKey('users.username'))
    review_id = db.Column(db.Integer, db.ForeignKey('books.id'))
    review = db.Column(db.String, nullable=False )

