import os
from flask import Flask , render_template, request,session,redirect
from flask_bootstrap import Bootstrap
from flaskr.db import getDbHelper
from flaskr.Database.UserDB import UserDB
from flaskr.Database.EventDB import EventDB
from flaskr.SessionGlobals import *
import datetime

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'database.db'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    #Database
    with app.app_context():
        dbHelper = getDbHelper()

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    Bootstrap(app)

    # Landing page
    @app.route('/')
    def Landing():
        return render_template("landing.html")

   # Game page
    @app.route('/flynn')
    def Fish():
        return render_template("flynn.html")

    #Login page =============
    @app.route('/login',methods=['GET'])
    def LoginGet():
        print("Get Login")
        return render_template("login.html")

    @app.route('/login', methods=['POST'])
    def Login():
        print("Post Login")
        result = dbHelper.Login(str(request.form['email']),str(request.form['password']))

        print(result)

        if result == dbHelper.LOGIN_SUCCESS:
            return redirect("/events")
        else:
            return render_template("login.html",loginCheck =result)

    #Registration page 
    @app.route('/register', methods=['GET', 'POST'])
    def Register():
        if request.method == "POST":
            newUser = UserDB(str(request.form['email']),str(request.form['password']),str(request.form['userType']))
            result = dbHelper.AddUser(newUser)
            print(result)
            if result == dbHelper.REGISTRATION_SUCCESS:
                #called when registration is a success.
                return render_template("register.html",registrationCheck = result)
            else:
                #called when registration was a failure.
                return render_template("register.html",registrationCheck = result)

        #called when first get on the page
        return render_template("register.html")

    #Profile for creator 
    @app.route('/creator')
    def Creator():
        listOfEvents = dbHelper.getAllEvent()
        ##listOfEvents = [eventDic1,eventDic2]
        return render_template("auth/creator.html", listOfEvents = listOfEvents)

    @app.route('/creator', methods=["POST"])
    def CreatorPost():
        event = EventDB()
        event.name = request.form[EventDB.dbName]
        event.description = request.form[EventDB.dbDescription]
        event.address = request.form[EventDB.dbAddress]
        event.creatorID = session[SessUserID]
        event.startTime = request.form[EventDB.dbStartTime]
        event.endTime = request.form[EventDB.dbEndTime]
        event.date = request.form[EventDB.dbDate]
        event.creationDate = datetime.datetime.now().strftime("%Y-%m-%d")
        event.creationTime = datetime.datetime.now().strftime("%H:%M")

        dbHelper.AddEvent(event)

        return Creator()


    #Profile for user
    @app.route('/user')
    def User():
        listOfEvents = dbHelper.getAllEvent()
        return render_template("user/user.html", listOfEvents = listOfEvents)

    #Events page
    @app.route('/events')
    def Events():
        if session.get(SessLoggedIn):
            if session[SessUserType] == UserDB.dbRoleUser:
                print("User")
                return redirect("/user")
            elif session[SessUserType] == UserDB.dbRoleHost:
                print("Host")
                return redirect("/creator")
            elif session[SessUserType] == UserDB.dbRoleAdmin:
                print("Admin")
                return redirect("/events")

        listOfEvents = dbHelper.getAllEvent()
        return render_template("events.html", listOfEvents = listOfEvents)


    @app.route('/logout')
    def Logout():
        session.clear()
        return Landing()

    

    return app

