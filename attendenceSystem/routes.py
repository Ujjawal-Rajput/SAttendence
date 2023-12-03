import os,secrets,cv2,csv
from PIL import Image
from flask import Flask, redirect, render_template, request,jsonify, url_for, session, flash
from attendenceSystem import app, db, bcrypt#, scheduler
from attendenceSystem.forms import RegistrationForm, LoginForm, UpdateAccountForm
from attendenceSystem.models import User, MarkAttendence, Auth
from flask_login import login_user, current_user, logout_user, login_required
import face_recognition
import numpy as np
from datetime import datetime
import geopy.distance
# from sqlalchemy import text ,MetaData, Column, String, Date, DateTime, Integer, Table
# from sqlalchemy.schema import MetaData
# from apscheduler.schedulers.background import BackgroundScheduler


# posts = [
#     {
#         'author': 'Corey Schafer',
#         'title': 'Blog Post 1',
#         'content': 'First post content',
#         'date_posted': 'April 20, 2018'
#     },
#     {
#         'author': 'Jane Doe',
#         'title': 'Blog Post 2',
#         'content': 'Second post content',
#         'date_posted': 'April 21, 2018'
#     }
# ]





# def auth():
#     if current_user.is_authenticated and current_user.section != 'Coordinator':
#         return True
#     return False

@app.route("/studentPage")
def studentPage():
    if current_user.is_authenticated and current_user.section != 'Coordinator':
        user = MarkAttendence.query.filter_by(rollno=current_user.rollno)
        data = [{'date':'mark','attendence': i.mark,'time':i.date_posted} for i in user]
        check = Auth.query.filter_by(section=current_user.section)
        for i in check:
            value = i.allow_or_not
            lecture = i.current_lecture
        print(value)
        return render_template("studentPage.html",data=data,can=value,lecture=lecture) 
    return redirect(url_for('login'))

@app.route("/coordinatorPage")
def coordinatorPage():
    if current_user.is_authenticated and current_user.section == 'Coordinator':
        users = Auth.query.filter_by(section='2B')
        for i in users:
            valueis = i.allow_or_not
        return render_template("coordinatorPage.html",valueis = valueis)
        # student_list = MarkAttendence.query.filter_by(section='2B')
        # toshow=[]
        # for i in student_list:
            # toshow.append(i.user.name)
        # return render_template("coordinatorPage.html", data = toshow)
    return redirect(url_for('login'))




#all functions that are called by AJAX by post method only.
@app.route("/get_students", methods=['POST'])
def get_students():
    if current_user.is_authenticated and current_user.section == 'Coordinator':
        data = request.get_json()
        # print(data)
        users = MarkAttendence.query.filter_by(section=data['selectedValue'])
        # Extract the values and create a list of dictionaries
        user_data = [{'rollno':i.rollno,'name': i.user.name, 'attendence': i.mark,'time':i.date_posted} for i in users]
        # Convert the list of dictionaries to JSON
        json_data = {'users': user_data}
        # print(json_data)
        # import time
        # time.sleep(1)
        return json_data
    else:
        return {"error":'Fetching failed...'}

@app.route("/toggle_true_false", methods=['POST'])
def toggle_true_false():
    if current_user.is_authenticated and current_user.section == 'Coordinator':
        data = request.get_json()
        users = Auth.query.filter_by(section=data['section'])
        now = False
        for i in users:
            print(i.allow_or_not)
            if i.allow_or_not:
                i.allow_or_not = False
                now = False
            else:
                i.allow_or_not = True
                now = True
        db.session.commit()
        # import time
        # time.sleep(1)
        return [now]
    else:
        return {"error":'Fetching failed...'}
    
@app.route("/check_true_or_false", methods=['POST'])
def check_true_false():
    if current_user.is_authenticated and current_user.section == 'Coordinator':
        data = request.get_json()
        # print(data)
        users = Auth.query.filter_by(section=data['selectedValue'])
        for i in users:
            valueis = i.allow_or_not
        return [valueis]
    else:
        return {"error":'Fetching failed...'}
    
@app.route("/coordinatorMark", methods=['POST'])
def coordinatorMark():
    if current_user.is_authenticated and current_user.section == 'Coordinator':
        data = request.get_json()
        user = MarkAttendence.query.filter_by(rollno=data['rollno'])
        binary = '0'
        user_data=[]
        for i in user:
            integer_list = [bit for bit in i.mark]
            if data['count'] == 0:
                integer_list[data['lecture']-1] = '1'
                binary = '1'
            else:
                integer_list[data['lecture']-1] = '0'
                binary = '0'
            i.date_posted=data['time']

            a = ''.join(integer_list)
            i.mark = a
            user_data = [binary,i.date_posted]

        db.session.commit()
        json_data = {'data': user_data}
        # print(json_data)
        return json_data
    else:
        return {"error":'marking failed...'}










@app.route("/about")
def about():
    return render_template('about.html', title='About')

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        # print(current_user.section)
        if current_user.section == 'Coordinator':
            return redirect(url_for('coordinatorPage'))
        else:
            return redirect(url_for('studentPage'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        picture_file = save_picture(form.upload.data)
        user = User(rollno=form.rollno.data,name=form.name.data,image_file=picture_file, section=form.section.data ,email=form.email.data, password=hashed_password)
        add_in_year = MarkAttendence(rollno=form.rollno.data, section=form.section.data)
        # year = int(form.section.data[0])
        # print(year)
        # if year==1:
        #     add_in_year = Year_1(rollno=form.rollno.data, section=form.section.data)
        # elif year==2:
        #     add_in_year = Year_2(rollno=form.rollno.data, section=form.section.data)
        # elif year==3:
        #     add_in_year = Year_3(rollno=form.rollno.data, section=form.section.data)
        # elif year==4:
        #     add_in_year = Year_4(rollno=form.rollno.data, section=form.section.data)
        
        db.session.add(user)
        db.session.add(add_in_year)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


# def add_column_daily():
#     # Generate a unique column name based on the current date
#     # column_name = f'{datetime.now().strftime("%Y%m%d")}'
#     # print(column_name)

#     # Check if the column already exists
#     # table_name = 'MarkAttendence'
#     # metadata = db.metadata
#     # engine = db.engine

#     # # Reflect the existing table structure
#     # metadata.reflect(bind=engine)
#     # table = metadata.tables.get(table_name)

#     new_column_name = f'{datetime.now().strftime("%d-%m-%Y")}'

    
#     MarkAttendence.__table__.reflect()
#     if new_column_name not in MarkAttendence.__table__.columns:
#         sql_expression = text(f"ALTER TABLE MarkAttendence ADD COLUMN {new_column_name} VARCHAR(50)")
#         db.session.execute(sql_expression)
#         db.session.commit()
#         # new_column = Column(new_column_name, String)
#         # new_column.create(table)
#         print("2. ",new_column_name)
#     print("1. ",new_column_name)


# scheduler = BackgroundScheduler()
# scheduler.add_job(add_column_daily, trigger='cron', hour=00, minute=2)
# scheduler.start()




# here i a problem in my smart attendence website, as name suggests i am taking attendence via online portal. the problem arises when i am host my website, but in works fine on localhost, problem is that when i login into a account using my pc, i also automatically logins into the same account in another device mobile, i am using flask , flask_login in backend. my login and register route are as below, 


@app.route("/", methods=['GET', 'POST'])
@app.route("/login", methods=['GET', 'POST'])
def login():
    # print(current_user)
    # if current_user.is_authenticated and current_user.section != 'Coordinator':
    #     # print(current_user.section)
    #     return redirect(url_for('studentPage'))
    # elif current_user.is_authenticated and current_user.section == 'Coordinator':
    #     return redirect(url_for('coordinatorPage'))
    if current_user.is_authenticated:
        if current_user.section == 'Coordinator':
            return redirect(url_for('coordinatorPage'))
        else:
            # add_column_daily()
            return redirect(url_for('studentPage'))
    form = LoginForm()
    if form.validate_on_submit():
        useris = User.query.filter_by(rollno=form.id.data).first()
        # if (form.id.data==123 and form.password.data==000):
        #     login_user(user, remember=form.remember.data)
        #     return redirect(url_for('coordinatorPage'))
        # if form.id.data == 2202310100107 and form.password.data == 'password':
        if useris and bcrypt.check_password_hash(useris.password, form.password.data):
            if (useris.section=="Coordinator"):
                if useris.rollno==123:
                    login_user(useris, remember=form.remember.data)
                    return redirect(url_for('coordinatorPage'))
                return "you have registered as a coordinator, but in reality you are not. "
            login_user(useris, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('studentPage'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
@login_required
def logout():
    # user = current_user
    # user.authenticated = False
    # db.session.add(user)
    # db.session.commit()
    logout_user()
    # logout_user()
    return redirect(url_for('studentPage'))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    picture_path = os.path.join(app.root_path, 'static/img', picture_fn)
    output_size = (300, 300)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    # if current_user.is_authenticated and current_user.section == 'Coordinator':
    # change below data according to the coordinator.
    form = UpdateAccountForm()
    if form.validate_on_submit():
        # user = User.query.filter_by(rollno=form.rollno.data).first()
        # if bcrypt.check_password_hash(current_user.password, form.password.data):
        current_user.rollno = form.rollno.data
        current_user.name = form.name.data
        current_user.section = form.section.data
        current_user.email = form.email.data
        if form.upload.data:
            picture_file = save_picture(form.upload.data)
            current_user.image_file = picture_file
            # print(current_user.image_file)
            # path = os.path.join(app.config["IMAGE_UPLOADS"], current_user.image_file)  
            # os.remove(path)
            # path = os.path.join( image.filename)
            # if os.path.exists(url_for('static', filename='img/' + current_user.image_file)):
            # os.remove(url_for('static', filename='img/' + current_user.image_file))
            # print(current_user.image_file)
        # current_user.password = form.password.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
        # else:
        #     flash('Something went wrong' ,'danger')
    elif request.method == 'GET':
        form.rollno.data = current_user.rollno
        form.name.data = current_user.name
        form.section.data = current_user.section
        form.email.data = current_user.email
    image_file = url_for('static', filename='img/' + current_user.image_file)
    return render_template('account.html', title='Account',image_file=image_file, form=form)


def is_student_in_classroom(student_coordinates,class_coordinates):
    threshold_distance=0.08 #in km
    distance = geopy.distance.distance(class_coordinates,student_coordinates)
    print(distance)
    return distance <= threshold_distance

@app.route('/process_frame', methods=['POST'])
def process_frame():
    check = Auth.query.filter_by(section=current_user.section)
    for i in check:
        value = i.allow_or_not
        if value == False:
            return jsonify({"message": "coordinator has disabled attendence."})

    student_latitude = request.form.get("latitude")
    student_longitude = request.form.get("longitude")
    print(student_latitude)
    print(student_longitude)
    # students_latitude=28.682085
    # student_longitude=77.341755
    student_coordinates=(student_latitude,student_longitude)
    # class_coordinates=(28.73632768718917, 77.48282227507165) #rd
    class_coordinates=(28.681776187231414, 77.34231361360732) #bansal kirana store
    #28.682080771681647, 77.34172937700261

    if is_student_in_classroom(student_coordinates,class_coordinates):
        pass
    else:
        return jsonify({"message": "Not in college"})
    
    image_path=os.path.join(app.root_path, 'static/img', current_user.image_file)
    user_image = face_recognition.load_image_file(image_path) #session user image-profile
    user_encoding = face_recognition.face_encodings(user_image)[0]

    known_face_encoding = [user_encoding]
    known_faces_names = [current_user.name] #session user name-username
    students = known_faces_names.copy()
    try:
        # Receive and process video frames from JavaScript
        frame_data = request.files['frame']  # Get the frame data from the client

        if frame_data is None:
            return jsonify({"error": "No frame data received"})

        # Read the frame data and decode it
        frame_bytes = frame_data.read()
        nparr = np.frombuffer(frame_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # Check if the frame is empty or not successfully decoded
        if frame is None:
            return jsonify({"error": "Invalid frame format"})

        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
        face_names = []

        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(known_face_encoding, face_encoding)
            name = ''
            face_distance = face_recognition.face_distance(known_face_encoding, face_encoding)
            best_match_index = np.argmin(face_distance)
            if matches[best_match_index]:
                name = known_faces_names[best_match_index]

            face_names.append(name)
            # if name in students:
            #     # students.remove(name)
            #     print(students)
            #     current_time = now.strftime("%H-%M-%S")
            #     lnwriter.writerow([name, current_time])
        print(face_names)
        if face_names==['']:
            return jsonify({"message": "Face isn't matching"})
        elif face_names==[]:
            return jsonify({"message": "face is out of focus"})
        

        
        user = MarkAttendence.query.filter_by(rollno=current_user.rollno)
        my_class = Auth.query.filter_by(section=current_user.section)
        for j in my_class:
            current_lecture = j.current_lecture

        # print(current_user.section)
        for i in user:
            # print(i.mark)
            integer_list = [bit for bit in i.mark]
            integer_list[current_lecture-1] = '1'
            a = ''.join(integer_list)
            i.mark = a
        db.session.commit()

        return jsonify({"recognized_faces": face_names})
        # return render_template('studentPage.html')
        # flash('Present marked', 'success')
    except Exception as e:
        return jsonify({"error": str(e)})