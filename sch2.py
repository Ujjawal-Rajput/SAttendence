from datetime import datetime

# Define the schedule of lectures with their start times
lecture_schedule = {
    1: "09:10",  # 9:10 AM
    2: "10:00",  # 10:00 AM
    3: "11:00",  # 11:00 AM
    4: "11:50",  # 11:50 AM
    5: "12:40",  # 12:40 PM
    # 6: "13:30",  # 1:30 PM
    6: "14:20",  # 2:20 PM
    7: "15:10",  # 3:10 PM
    8: "16:00",  # 4:00 PM
    # 9: "16:50"  # 4:50 PM
}


# Get the current time
current_time = "09:09"
# current_time = datetime.now().strftime("%H:%M")

# Determine the current lecture based on the schedule
current_lecture_number = None
for lecture_number, start_time in lecture_schedule.items():
    # if current_time >= "16:50":
    #     current_lecture_number = None
    if current_time >= start_time and current_time<"16:50":
        current_lecture_number = lecture_number

# If the current time is after the last lecture, set to the last lecture
# if current_lecture_number is None:
#     current_lecture_number = None
    # current_lecture_number = len(lecture_schedule)

# Now, you can use current_lecture_number to update attendance as before
attendance_string = "00000000"
if current_lecture_number is not None:
    attendance_string = attendance_string[:current_lecture_number - 1] + "1" + attendance_string[current_lecture_number:]
print("Updated Attendance:", attendance_string,"current_lecture_number:",current_lecture_number)






'''
@app.route("/studentPage")
def studentPage():
    if current_user.is_authenticated and current_user.section != 'Coordinator':
        user = MarkAttendence.query.filter_by(rollno=current_user.rollno).first()
        from collections import deque
        from itertools import islice
        # Convert the dictionary items to a deque
        items_deque = deque(user.mark.items())

        # Get the last 30 key-value pairs using islice
        last_30_pairs = dict(islice(items_deque, -30, None))
        # if i.mark.get(datetime.now().strftime('%d/%m/%Y'))==None:
        #         i.mark[datetime.now().strftime('%d/%m/%Y')] = "00000000" i.mark[list(i.mark.keys())[-1]]
        data = [{'attendence':last_30_pairs,'time':user.date_posted}]
        # data = [{'date':list(i.mark.keys())[-1] if i.mark.get(datetime.now().strftime('%d/%m/%Y'))!=None else datetime.now().strftime('%d/%m/%Y'),'attendence': i.mark[list(i.mark.keys())[-1]] if i.mark.get(datetime.now().strftime('%d/%m/%Y'))!=None else "00000000"
        #          ,'time':i.date_posted} for i in user]
        check = Auth.query.filter_by(section=current_user.section).first()
        value = check.allow_or_not
        lecture = current_lecture()
        # lecture = check.current_lecture
        # print(value)
        return render_template("studentPage.html",data=data,can=value,lecture=lecture) 
    return redirect(url_for('login'))
'''


'''
this code was at line no. 28 in studentPage.html
<h3 class="mt-5">Today </h3>
    <div class="coordination">
        {% for i in range(lecture) %}
        {% if data[0].attendence[i]=='1' %}
        <span class="badge text-bg-info">Present</span>
        <span>in Lec-{{ loop.index }}</span>
        {% else %}
        <span class="badge text-bg-danger">Absent</span>
        <span>in Lec-{{ loop.index }}</span>
        {% endif %}
        {% endfor %}
    </div>
'''