from attendenceSystem import app, db
from attendenceSystem.models import User, MarkAttendence, Auth

with app.app_context():
    user = User.query.all()
    attendence = MarkAttendence.query.all()
    auth = Auth.query.all()

    print("=======================================User Table====================================================================")
    for i in user:
        print(i)

    print("=======================================MarkAttendence Table====================================================================")
    for i in attendence:
        print(i)

    print("=======================================Auth Table====================================================================")
    for i in auth:
        print(i)