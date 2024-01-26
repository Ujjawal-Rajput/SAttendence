import os,secrets,cv2,csv
from PIL import Image
from flask import Flask, redirect, render_template, request,jsonify, url_for, session, flash, make_response
from attendenceSystem import app, db, bcrypt#, scheduler
from attendenceSystem.forms import RegistrationForm, LoginForm, UpdateAccountForm
from attendenceSystem.models import User, MarkAttendence, Auth
from flask_login import login_user, current_user, logout_user, login_required
import face_recognition
import numpy as np
from datetime import datetime
import time
import geopy.distance
import threading
from sqlalchemy.orm import attributes
# import schedule
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

@app.errorhandler(404)
def not_found(error):
    resp = make_response(render_template('error.html'), 404)
    resp.headers['X-Something'] = 'A value'
    return resp


@app.route("/studentPage")
def studentPage():
    if current_user.is_authenticated and current_user.section != 'Coordinator':
        user = MarkAttendence.query.filter_by(rollno=current_user.rollno).first()

        # This approach is more efficient than using list(my_dict.items())[-30:] for large dictionaries
        from collections import deque
        items_deque = deque(user.mark.items(), maxlen=30)
        last_30_pairs = dict(items_deque)

        data = [{'attendence':last_30_pairs,'time':user.date_posted}]

        # today = datetime.now().strftime('%d/%m/%Y')
        # if today<"25/01/2024":
        #     print("small")
        # else:
        #     print("big")

        
        # if i.mark.get(datetime.now().strftime('%d/%m/%Y'))==None:
        #         i.mark[datetime.now().strftime('%d/%m/%Y')] = "00000000" i.mark[list(i.mark.keys())[-1]]
        # data = [{'date':list(i.mark.keys())[-1] if i.mark.get(datetime.now().strftime('%d/%m/%Y'))!=None else datetime.now().strftime('%d/%m/%Y'),'attendence': i.mark[list(i.mark.keys())[-1]] if i.mark.get(datetime.now().strftime('%d/%m/%Y'))!=None else "00000000"
        #          ,'time':i.date_posted} for i in user]

        check = Auth.query.filter_by(section=current_user.section).first()
        can = check.allow_or_not
        lecture = current_lecture()

        return render_template("studentPage.html",data=data,can=can,lecture=lecture) 
    return redirect(url_for('login'))

@app.route("/coordinatorPage")
def coordinatorPage():
    if current_user.is_authenticated and current_user.section == 'Coordinator':
        users = Auth.query.filter_by(section='2B').first()
        return render_template("coordinatorPage.html",valueis = users.allow_or_not, lecture = users.current_lecture)
        # student_list = MarkAttendence.query.filter_by(section='2B')
        # toshow=[]
        # for i in student_list:
            # toshow.append(i.user.name)
        # return render_template("coordinatorPage.html", data = toshow)
    return redirect(url_for('login'))

def setToFalse_after_5(data):
    print(data)
    with app.app_context():
        user = Auth.query.filter_by(section=data).first()
        user.allow_or_not = False
        db.session.commit()


#all functions that are called by AJAX by post method only.
@app.route("/get_students", methods=['POST'])
def get_students():
    if current_user.is_authenticated and current_user.section == 'Coordinator':
        data = request.get_json()
        # print(data)
        users = MarkAttendence.query.filter_by(section=data['selectedValue'])
        classes = Auth.query.filter_by(section=data['selectedValue']).first()
        coordinates = classes.coordinates['list']
        # Extract the values and create a list of dictionaries
        user_data = [{'rollno':i.rollno,'name': i.user.name, 'attendence': i.mark[list(i.mark.keys())[-1]] if i.mark.get(datetime.now().strftime('%d/%m/%Y'))!=None else "00000000",'time':i.date_posted} for i in users]
        # user_data = [{'rollno':i.rollno,'name': i.user.name, 'attendence': i.mark[enter current date here],'time':i.date_posted} for i in users]
        # Convert the list of dictionaries to JSON
        # print(user_data)
        json_data = {'users': user_data,'coordinates':coordinates}
        # print(json_data)
        # import time
        # time.sleep(2)
        return json_data
    else:
        return {"error":'Fetching failed...'}

@app.route("/toggle_true_false", methods=['POST'])
def toggle_true_false():
    if current_user.is_authenticated and current_user.section == 'Coordinator':
        data = request.get_json()
        users = Auth.query.filter_by(section=data['section']).first()
        now = False
        timeis=None
        timeris = threading.Timer(300, setToFalse_after_5, args=(data['section'],) )
        print(type(timeris))
        # for i in users:
            # print(i.allow_or_not)
            # timer = None
        if users.allow_or_not:
            users.allow_or_not = False
            now = False
            timeris.cancel()
        else:
            users.allow_or_not = True
            now = True
            timeris.start()
            # timeris = threading.Timer(10, setToFalse_after_5, args=(data['section'],) )
            # setToFalse_after_5()
        users.date_posted = datetime.now().strftime("%H:%M:%S")
        timeis = users.date_posted
        db.session.commit()
        # import time
        # time.sleep(1)
        return [now,timeis]
    else:
        return {"error":'Fetching failed...'}
    
@app.route("/check_true_or_false", methods=['POST'])
def check_true_false():
    if current_user.is_authenticated and current_user.section == 'Coordinator':
        data = request.get_json()
        # print(data)
        users = Auth.query.filter_by(section=data['selectedValue']).first()
        valueis = users.allow_or_not
        timeis = users.date_posted
        return [valueis,timeis]
    else:
        return {"error":'Fetching failed...'}
    
@app.route("/coordinatorMark", methods=['POST'])
def coordinatorMark():
    if current_user.is_authenticated and current_user.section == 'Coordinator':
        data = request.get_json()
        user = MarkAttendence.query.filter_by(rollno=data['rollno']).first()
        binary = '0'
        user_data=[]
        # for i in user:
        # print(i)
        if user.mark.get(datetime.now().strftime('%d/%m/%Y'))==None:
            user.mark[datetime.now().strftime('%d/%m/%Y')] = "00000000"
        #     db.session.commit()
        #     print("entered into database")
        # print(i.mark)
        # value = i.mark.setdefault(datetime.now().strftime('%d/%m/%Y'),"00000000")
        # print(value)
        # print(i.mark)

        # currentDate=list(i.mark.keys())[-1]
        integer_list = [bit for bit in user.mark.get(datetime.now().strftime('%d/%m/%Y'))]
        if data['count'] == 0:
            integer_list[data['lecture']-1] = '1'
            binary = '1'
        else:
            integer_list[data['lecture']-1] = '0'
            binary = '0'
        user.date_posted=data['time']

        a = ''.join(integer_list)
        user.mark[datetime.now().strftime('%d/%m/%Y')] = a
        attributes.flag_modified(user, "mark")
        print(user.mark)
        user_data = [binary,user.date_posted]

        db.session.commit()
        json_data = {'data': user_data}
        # print(json_data)
        return json_data
    else:
        return {"error":'marking failed...'}



@app.route('/addCoordinate', methods=['POST'])
def addCoordinate():
    try:
        known_as = request.form.get('known_as')
        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')
        newCoordinates = (known_as, latitude, longitude)
        section = request.form.get('section')

        record = Auth.query.filter_by(section=section).first()
        for i in record.coordinates['list']:
            if known_as == i[0]:
                 return jsonify({'success': False})
        record.coordinates['list'].append(newCoordinates)
        attributes.flag_modified(record, "coordinates") #most important line related (to make changes in json field in sqlalchemy.)
        db.session.commit()
        return jsonify({'success': True,'coordinates': record.coordinates['list'], 'msg': 'coordinates added successfully.'})

    except Exception as e:
        return jsonify({'success': False, 'msg': f'Error: Something went wrong.'})
        # return jsonify({'success': False, 'msg': f'Error: {str(e)}'})

@app.route('/changeCoordinate', methods=['POST'])
def changeCoordinate():
    try:
        #{ section: selectedValue,choosedCoordinates : selectedOption }
        data = request.get_json()
        section = data['section']
        coordinates = eval(data['choosedCoordinates'])
        # print(coordinates)
        # print(type(coordinates))

        record = Auth.query.filter_by(section=section).first()
        record.coordinates['list'].remove(coordinates)
        record.coordinates['list'].insert(0, coordinates)
        # for i in record.coordinates['list']:
        #     print(i[0],coordinates[0])
        #     if i[0] == coordinates[0]:
        #         deletedCoordinates = i
        #         record.coordinates['list'].remove(i)
        # record.coordinates['list'].insert(0, deletedCoordinates)

        attributes.flag_modified(record, "coordinates") #most important line related (to make changes in json field in sqlalchemy.)
        db.session.commit()
        return jsonify({'success': True,'updatedCoordinates': record.coordinates['list'], 'msg': f'coordinates changed to "{coordinates[0]}" successfully.'})

    except Exception as e:
        return jsonify({'success': False, 'msg': f'Error: Unknown coordinates cannot be processed'})
        # return jsonify({'success': False, 'msg': f'Error: {str(e)}'})












#if student is absent then also insert {"17/2/2024":"00000000"} otherwise i am handling in last function of face matching or coordinator mark.

#now add feature to watch attendence history of students.
#also think about how to change lecture number (code should run every 50 min. after 9:10pm till 4:50)(watch schedule/threading modules)
#avoid taking attendence on sunday, saturday(after 1:30pm), holidays.




















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
    if current_user.is_authenticated and current_user.section == 'Coordinator':
        # change below data according to the coordinator.(coordinator when clicks on student rollno. then he must see student details.)
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
    else:
        return "only accessibly to coordinators"
    
def current_lecture():
     #Define the schedule of lectures with their start times
    # lecture_schedule = {
    #     1: "14:37",  # 9:10 AM
    #     2: "14:38",  # 10:00 AM
    #     3: "14:39",  # 11:00 AM
    #     4: "14:40",  # 11:50 AM
    #     5: "14:41",  # 12:40 PM
    #     # 6: "13:30",  # 1:30 PM #Lunch starts
    #     6: "14:42",  # 2:20 PM
    #     7: "14:42",  # 3:10 PM
    #     8: "14:42",  # 4:00 PM
    #     # 9: "14:42"  # 4:50 PM
    # }
    lecture_schedule = {
        1: "09:10",  # 9:10 AM
        2: "10:00",  # 10:00 AM
        3: "11:00",  # 11:00 AM
        4: "11:50",  # 11:50 AM
        5: "12:40",  # 12:40 PM
        # 6: "13:30",  # 1:30 PM #Lunch starts
        6: "14:20",  # 2:20 PM
        7: "15:10",  # 3:10 PM
        8: "16:00",  # 4:00 PM
        9: "16:50"  # 4:50 PM
    }

    # Get the current time
    current_time = datetime.now().strftime("%H:%M")
    # current_time = "09:15"
    
    # Determining the current lecture based on the schedule
    current_lecture_number = None
    for lecture_number, start_time in lecture_schedule.items():
        if current_time >= start_time and current_time < "16:50":
            current_lecture_number = lecture_number

    # If the current time is after the last lecture, set to the last lecture
    # if current_lecture_number is None:
    #     current_lecture_number = len(lecture_schedule)
    
    if current_lecture_number is not None:
        my_class = Auth.query.filter_by(section=current_user.section).first()
        my_class.current_lecture = current_lecture_number
        db.session.commit()
    
    return current_lecture_number


def is_student_in_classroom(student_coordinates,class_coordinates):
    threshold_distance=0.08 #in km
    distance = geopy.distance.distance(class_coordinates,student_coordinates)
    print(distance)
    return distance <= threshold_distance

@app.route('/process_frame', methods=['POST'])
def process_frame():
    check = Auth.query.filter_by(section=current_user.section).first()
    value = check.allow_or_not
    if value == False:
        return jsonify({"message": "coordinator has disabled attendence."})
    
    if current_lecture() is None:
        return jsonify({"message": "Allowed to mark only at college timing"})

    class_coordinates=(check.coordinates['list'][0][1], check.coordinates['list'][0][2]) #bansal kirana store
    # class_coordinates=(28.73632768718917, 77.48282227507165) #rd
    # class_coordinates=(28.681776187231414, 77.34231361360732) #bansal kirana store
    #28.682080771681647, 77.34172937700261

    student_latitude = request.form.get("latitude")
    student_longitude = request.form.get("longitude")
    print(student_latitude)
    print(student_longitude)
    student_coordinates=(student_latitude,student_longitude)
    # students_latitude=28.682085
    # student_longitude=77.341755

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
            return jsonify({"error": "No person frame received"})

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
        

        
        user = MarkAttendence.query.filter_by(rollno=current_user.rollno).first()
        # my_class = Auth.query.filter_by(section=current_user.section)
        # for j in my_class:
        #     current_lecture = j.current_lecture

        # print(current_user.section)
        # for i in user:
            # print(i.mark)
            # currentDate = list(i.mark.keys())[-1] #last key in {} in marks column.
        if user.mark.get(datetime.now().strftime('%d/%m/%Y'))==None: #if not in database then make one.
            user.mark[datetime.now().strftime('%d/%m/%Y')] = "00000000"



        # integer_list = [bit for bit in i.mark[datetime.now().strftime('%d/%m/%Y')]]
        # # list(i.mark.keys()[-1]) is fetching the key i.e. 25/12/2023 from  dict {}
        # integer_list[current_lecture-1] = '1'
        # a = ''.join(integer_list)

        attendance_string = user.mark[datetime.now().strftime('%d/%m/%Y')]
        a = attendance_string[: current_lecture() - 1] + "1" + attendance_string[current_lecture() : ]



        user.mark[datetime.now().strftime('%d/%m/%Y')] = a
        attributes.flag_modified(user, "mark") #most important line related (to make changes in json field in sqlalchemy.)
        # print(i)
        db.session.commit()

        return jsonify({"recognized_faces": face_names})
        # return render_template('studentPage.html')
        # flash('Present marked', 'success')
    except Exception as e:
        return jsonify({"error": str(e)})