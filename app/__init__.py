from flask import Flask             #facilitate flask webserving
from flask import render_template   #facilitate jinja templating
from flask import request           #facilitate form submission
from flask import session           #facilitate user sessions
from flask import redirect
from os import urandom
from utils.db import createBlogPost
from utils.db import loadHomePage
from utils.db import pullUserData
from utils.db import loadEdit

from utils.db import initializeDatabase
from utils.auth import AuthService

app = Flask(__name__)

# from utils.db import initializeDatabase;

auth = AuthService()

@app.route("/")
def disp_loginpage():
    currentUser = auth.currentUser().payload

    if currentUser:
        return render_template('homePage.html', blogs=loadHomePage())

    return render_template( 'login.html' ) # Render the login template


@app.route("/login", methods=['GET', 'POST'])
def authenticate():
    # The requests property contains the values property. The value property contains
    # data from both requests.args and requests.form.

    if request.method == "GET": #for when you refresh the website
        return disp_loginpage()
    else: #when you log in from /
        username = request.values['username']
        password = request.values['password']

        if auth.login(username, password).success:
            return redirect("/")
        else:
            return render_template('login.html', error='Incorrect username or password')

@app.route("/signup", methods=['GET', 'POST'])
def register():
    if request.method == "GET":
        return render_template('register.html')
    elif request.method == "POST":  #Takes values entered by user via request.values
        username = request.values['username']
        displayName = request.values['displayName']
        password = request.values['password']
        auth.register(username, displayName, password) #Appends user info to a database
        return redirect("/login") #After registering, brings you to login

@app.route("/editBlog/<string:id>", methods = ['GET', 'POST'])
def editBlog(id):
    blog = loadEdit(id)
    if request.method == "GET":
        return render_template('editBlog.html', postTitle = blog[3], postContent = blog[4])
    elif request.method == "POST":
        return "test"

@app.route("/myBlog")
def myBlog():
    userID = dict(auth.currentUser().payload)["username"]
    return render_template('myBlog.html', blogs=pullUserData(userID))

@app.route("/createPosts", methods =['GET', 'POST'])
def createPost():
    if request.method == "GET":
        return render_template('createPosts.html')
    elif request.method == "POST": #When user submits, the values from the request are taken
        title = request.values['title']
        contents = request.values['contents']
        userID = dict(auth.currentUser().payload)["username"] #Finds the userID from database
        createBlogPost(title, contents, userID) #Appends values into database.
        return redirect("/myBlog")

@app.route("/logout")
def logout():
    auth.logout() #function to logout
    return redirect("/") #redirect to login page

if __name__ == "__main__": #false if this file imported as module
    initializeDatabase()
    app.secret_key = urandom(32) # randomized secret key
    #enable debugging, auto-restarting of server when this file is modified
    app.debug = True
    app.run()
