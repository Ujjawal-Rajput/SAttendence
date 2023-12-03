from datetime import datetime
from attendenceSystem import db, login_manager
from flask_login import UserMixin



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



class User(db.Model, UserMixin):
    # add p and a column also.
    # __tablename__ = 'User'  # Specify the actual table name in your database
    id = db.Column(db.Integer, primary_key=True, unique=True) #unique number id
    rollno = db.Column(db.Integer, unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    section = db.Column(db.String(20),nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    attendence = db.relationship('MarkAttendence', backref='user', lazy=True)
    # year2 = db.relationship('Year_2', backref='user', lazy=True)
    # year3 = db.relationship('Year_3', backref='user', lazy=True)
    # year4 = db.relationship('Year_4', backref='user', lazy=True)
    # is_coordinator = db.Column(db.Boolean, default=False)
    # totalPresents = db.Column(db.Integer, nullable=False, default=0)
    # totalAbsents = db.Column(db.Integer, nullable=False, default=0)


    def __repr__(self):
        return f"User('{self.id}', '{self.rollno}', '{self.name}','{self.image_file}', '{self.section}', '{self.email}', '{self.password}','{self.attendence}')"


# class Post(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     title = db.Column(db.String(100), nullable=False)
#     date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
#     content = db.Column(db.Text, nullable=False)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.rollno'), nullable=False)

#     def __repr__(self):
#         return f"Post('{self.title}', '{self.date_posted}')"
    




class MarkAttendence(db.Model):
    # __tablename__ = 'Post'  # Specify the actual table name in your database
    id = db.Column(db.Integer, primary_key=True)
    rollno = db.Column(db.Integer, db.ForeignKey('user.rollno'), unique=True, nullable=False)
    # user_id = db.Column(db.Integer, db.ForeignKey('user.rollno'), nullable=False)
    section = db.Column(db.String(20),nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    mark = db.Column(db.String(20),default="00000000")
    # mark = db.Column(db.String(20),default=0)

    def __repr__(self):
        return f"MarkAttendence('{self.rollno}','{self.section}', '{self.date_posted}', '{self.mark}')"

class Auth(db.Model):
    # __tablename__ = 'Post'  # Specify the actual table name in your database
    id = db.Column(db.Integer, primary_key=True)
    section = db.Column(db.String(20), db.ForeignKey('user.section'), nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    allow_or_not = db.Column(db.Boolean, nullable=False, default=False)
    current_lecture = db.Column(db.Integer, nullable=False, default=1)
    # all_coordinates
    # selected_coordinate
    


    # user_id = db.Column(db.Integer, db.ForeignKey('user.rollno'), nullable=False)

    def __repr__(self):
        return f"Auth('{self.id}','{self.section}', '{self.date_posted}', '{self.allow_or_not},'{self.current_lecture}')"
    







# class Year_1(db.Model):
#     # __tablename__ = 'Post'  # Specify the actual table name in your database
#     id = db.Column(db.Integer, primary_key=True)
#     rollno = db.Column(db.Integer, db.ForeignKey('user.rollno'), unique=True, nullable=False)
#     # user_id = db.Column(db.Integer, db.ForeignKey('user.rollno'), nullable=False)
#     section = db.Column(db.String(20),nullable=False)
#     date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


#     def __repr__(self):
#         return f"Year_1('{self.rollno}', '{self.user_id}','{self.section}', '{self.date_posted}')"
    


# class Year_2(db.Model):
#     # __tablename__ = 'Post'  # Specify the actual table name in your database
#     id = db.Column(db.Integer, primary_key=True)
#     rollno = db.Column(db.Integer, db.ForeignKey('user.rollno'), unique=True, nullable=False)
#     # user_id = db.Column(db.Integer, db.ForeignKey('user.rollno'), nullable=False)
#     section = db.Column(db.String(20),nullable=False)
#     date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


#     def __repr__(self):
#         return f"Year_2('{self.rollno}', '{self.user_id}','{self.section}', '{self.date_posted}')"
    


# class Year_3(db.Model):
#     # __tablename__ = 'Post'  # Specify the actual table name in your database
#     id = db.Column(db.Integer, primary_key=True)
#     rollno = db.Column(db.Integer, db.ForeignKey('user.rollno'), unique=True, nullable=False)
#     # user_id = db.Column(db.Integer, db.ForeignKey('user.rollno'), nullable=False)
#     section = db.Column(db.String(20),nullable=False)
#     date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


#     def __repr__(self):
#         return f"Year_3('{self.rollno}', '{self.user_id}','{self.section}', '{self.date_posted}')"
    


# class Year_4(db.Model):
#     # __tablename__ = 'Post'  # Specify the actual table name in your database
#     id = db.Column(db.Integer, primary_key=True)
#     rollno = db.Column(db.Integer, db.ForeignKey('user.rollno'), unique=True, nullable=False)
#     # user_id = db.Column(db.Integer, db.ForeignKey('user.rollno'), nullable=False)
#     section = db.Column(db.String(20),nullable=False)
#     date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


#     def __repr__(self):
#         return f"Year_4('{self.rollno}', '{self.user_id}','{self.section}', '{self.date_posted}')"




#need location table and section table(6 sections)
#function to add a section (new table) and set his coordinator (no need to set this),ask students to register themselves.

#add functionaliy to change or set class coordinates (because classes can be merged , changed)

#dlib @ file:///C:/Users/rujja/OneDrive/Desktop/attendence/dlib-19.24.1-cp311-cp311-win_amd64.whl#sha256=6f1a5ee167975d7952b28e0ce4495f1d9a77644761cf5720fb66d7c6188ae496