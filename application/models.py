from flask_login import UserMixin
from .database import db
from sqlalchemy_serializer import SerializerMixin

class Author(db.Model, SerializerMixin):
    __tablename__ = 'authors'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)

class Section(db.Model, SerializerMixin):
    __tablename__ = 'sections'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    date_created = db.Column(db.DateTime, nullable=False, server_default=db.text("CURRENT_TIMESTAMP"))
    description = db.Column(db.Text, nullable=False)



class User(db.Model, SerializerMixin, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.Text, nullable=False)
    lname = db.Column(db.Text, nullable=False)
    username = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.text("CURRENT_TIMESTAMP"))
    role = db.Column(db.String(255), nullable=False, server_default=db.text("student"))
    tier = db.Column(db.Integer, nullable=False, server_default=db.text("0"))
    email = db.Column(db.String(255), nullable=False)
    def get_id(self):
        return(self.username)


class Book(db.Model, SerializerMixin):
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    rating = db.Column(db.Integer, default=0)
    reads = db.Column(db.Integer, default=0)
    #section = db.Column(db.ForeignKey('sections.id'), nullable=False)
    desc = db.Column(db.Text)
    date_created = db.Column(db.DateTime, nullable=False, server_default=db.text("CURRENT_TIMESTAMP"))
    #section1 = db.relationship('Section')


class Issued(db.Model, SerializerMixin):
    __tablename__ = 'issued'

    user = db.Column(db.ForeignKey('users.id'), primary_key=True)
    book = db.Column(db.ForeignKey('books.id'), primary_key=True)
    start = db.Column(db.DateTime, nullable=False, server_default=db.text("CURRENT_TIMESTAMP"))

    book1 = db.relationship('Book')
    user1 = db.relationship('User')


class Rating(db.Model, SerializerMixin):
    __tablename__ = 'rating'

    user = db.Column(db.ForeignKey('users.id'), primary_key=True)
    book = db.Column(db.ForeignKey('books.id'), primary_key=True)
    score = db.Column(db.Integer, nullable=False)

    book1 = db.relationship('Book')
    user1 = db.relationship('User')


class Request(db.Model, SerializerMixin):
    __tablename__ = 'requests'

    user = db.Column(db.ForeignKey('users.id'), primary_key=True)
    book = db.Column(db.ForeignKey('books.id'), primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.text("CURRENT_TIMESTAMP"))

    book1 = db.relationship('Book')
    user1 = db.relationship('User')

class Section_content(db.Model, SerializerMixin):
    __tablename__= 'section_content'

    book_id = db.Column(db.ForeignKey('books.id'), primary_key=True)
    section_id = db.Column(db.ForeignKey('sections.id'), primary_key=True)

    section_id1 = db.relationship('Section')
    book_id1 = db.relationship('Book')

class Authorship(db.Model, SerializerMixin):
    __tablename__= 'authorship'

    book_id = db.Column(db.ForeignKey('books.id'), primary_key=True)
    author_id = db.Column(db.ForeignKey('authors.id'), primary_key=True)

    author_id1 = db.relationship('Author')
    book_id1 = db.relationship('Book')

class History(db.Model, SerializerMixin):
    __tablename__ = 'history'

    user = db.Column(db.ForeignKey('users.id'), primary_key=True)
    book = db.Column(db.ForeignKey('books.id'), primary_key=True)
    start = db.Column(db.DateTime, primary_key=True)
    end = db.Column(db.DateTime, server_default=db.text("CURRENT_TIMESTAMP"))
    book1 = db.relationship('Book')
    user1 = db.relationship('User')

class Policy(db.Model, SerializerMixin):
    __tablename__ = 'policy'
    name = db.Column(db.Text, nullable=False, primary_key=True)
    value = db.Column(db.Integer, nullable=False)