from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
# from flask_apscheduler import APScheduler
from flask_wtf.csrf import CSRFProtect


app = Flask(__name__)
# app.secret_key = '57678y98696ce0c676dfd655860ba245'
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sites.db'
# app.config["WTF_CSRF_CHECK_DEFAULT"] = True
app.config["WTF_CSRF_CHECK_DEFAULT"] = False
app.config["IMAGE_UPLOADS"] = 'static/img/'
db = SQLAlchemy(app)
app.app_context().push()
bcrypt = Bcrypt(app)

csrf = CSRFProtect(app)
# csrf.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)
# scheduler = APScheduler(app)
# scheduler.start()
# csrf = CSRFProtect(app)


from attendenceSystem import routes          #this line should be present here



# bcrypt==4.0.1
# blinker==1.6.2
# click==8.1.7
# colorama==0.4.6
# dnspython==2.4.2
# dlib==19.24.2
# email-validator==2.0.0.post2
# face-recognition==1.3.0
# face-recognition-models==0.3.0
# Flask==2.3.3
# Flask-Bcrypt==1.0.1
# Flask-Login==0.6.3
# Flask-SQLAlchemy==3.1.1
# Flask-Uploads==0.2.1
# Flask-WTF==1.2.1
# geographiclib==2.0
# geopy==2.4.0
# greenlet==3.0.0
# idna==3.4
# itsdangerous==2.1.2
# Jinja2==3.1.2
# MarkupSafe==2.1.3
# numpy==1.26.1
# opencv-python==4.8.1.78
# Pillow==10.0.1
# SQLAlchemy==2.0.21
# typing_extensions==4.8.0
# Werkzeug==2.3.7
# WTForms==3.0.1
