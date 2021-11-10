from flask import Flask             #facilitate flask webserving
from flask import render_template   #facilitate jinja templating
from flask import request           #facilitate form submission
from flask import session           #facilitate user sessions
from flask import redirect
from os import urandom

from utils.auth import AuthService
from utils.db import *
app = Flask(__name__)

auth = AuthService()

@app.route("/")
def disp_loginpage():
    '''If user is logged in, then returns the home page. Otherwise, render login page.'''
    currentUserResponse = auth.currentUser()

    if currentUserResponse.success:
        currentUser = currentUserResponse.payload

        if currentUser: #Checks if user is logged in
            loadHomePageResponse = loadHomePage()
            if loadHomePageResponse.success:
                return render_template('homePage.html', blogs=loadHomePageResponse.payload)
            else:
                return render_template('homePage.html', blogs=None) # TODO: Add error handling

    return render_template( 'login.html' ) # Render the login template


@app.route("/login", methods=['GET', 'POST'])
def authenticate():
    '''If user does a get request, then return the login page. If it is a post request aka user logs in from login page, then check user credentials and will log in or deny based on provided credentials.
    The requests property contains the values property.
    The value property contains data from both requests.args and requests.form.'''

    if request.method == "GET": #for when you refresh the website
        return redirect('/')
    else: #when you log in from /
        username = request.values['username']
        password = request.values['password']

        if auth.login(username, password).success:
            return redirect("/")
        else:
            return render_template('login.html', error='Incorrect username or password')

@app.route("/signup", methods=['GET', 'POST'])
def register():
    '''If user does a get request (presses signup link from login page), then return registration page. Otherwise, creates a new user and add it to database for future authentication uses.'''
    if request.method == "GET":
        return render_template('register.html')
    elif request.method == "POST":  #Takes values entered by user via request.values
        username = request.values['username']
        displayName = request.values['displayName']
        password = request.values['password']

        registerResponse = auth.register(username, displayName, password) #Appends user info to a database

        if registerResponse.success:
            return redirect("/login") #After registering, brings you to login
        else:
            return render_template('register.html') 

@app.route("/editBlog/<string:id>", methods = ['GET', 'POST'])
def editBlog(id):
    '''If this is a get request (press the edit blog link for a blog post), then will return a page where you can change blog post contents. If this is a post request (user presses button to update a blog post), then edits will be applied to the blog post.'''
        
    if request.method == "GET":
        loadEditResponse = loadEdit(id) #finds the post id and fetches the corresponding blog list.
        
        if loadEditResponse.success:
            blog = loadEditResponse.payload
            return render_template('editBlog.html', id = id, postTitle = blog[3], postContent = blog[4]) #renders each blog with specific blog elements
        else:
            return render_template('editBlog.html', id = id, postTitle = "", postContent = "") # TODO: Replace with error message WE need an error not found
    elif request.method == "POST":
        currentUserResponse = auth.currentUser()

        if currentUserResponse.payload:
            userID = dict(currentUserResponse.payload)["username"]
            title = request.values['title']
            content = request.values['contents']
            
            editBlogPostResponse = editBlogPost(id, title, content, userID) #calls database function to update post
            
            if editBlogPostResponse.success:
                return redirect("/myBlog")
            else:
                return render_template('editBlog.html', id = id, postTitle = "", postContent = "") # TODO: Replace with error message 
        else:
            return redirect("/login")

@app.route("/deleteBlog/<string:id>", methods = ['GET']) # TODO: MAKE SURE ONLY CREATOR CAN DELETE
def deleteBlog(id):
    '''Deletes an existing blog post.'''
    if request.method == "GET":
        currentUserResponse = auth.currentUser()

        if currentUserResponse.payload:
            userID = dict(currentUserResponse.payload)["username"]
            deleteBlogPostResponse = deleteBlogPost(id, userID)

            if deleteBlogPostResponse.success: #finds post id in database and deletes it.
                return redirect("/myBlog")
            else:
                return redirect("/myBlog") # TODO: Add error message

@app.route("/myBlog")
def myBlog():
    '''Loads in all blog posts you have made.'''
    currentUserResponse = auth.currentUser()
    
    if currentUserResponse.success:
        userID = dict(currentUserResponse.payload)["username"]
        pullUserDataResponse = getAllBlogPostsByUser(userID)

        if pullUserDataResponse.success:
            return render_template('myBlog.html', blogs=pullUserDataResponse.payload) #finds userID and loads blog dictionary with userID
        else:
            return render_template('myBlog.html', blogs=None) #TODO: Add ERROR MESSAGE
    else:
        return redirect('/login')

@app.route("/search", methods = ['GET', 'POST'])
def loadSearchResult():
    '''Loads in the search result for a query. If search is refreshed, then it just shows a search box.'''
    if request.method == "GET":
        return render_template('search.html')
    elif request.method == "POST":
        query = request.values['query']

        searchResponse = search(query)
        
        if searchResponse.success:
            result = searchResponse.payload
            return render_template('search.html', query = query, blogs = result)
        else:
            return render_template('search.html')

@app.route("/post/<int:id>")
def viewPost(id):
    '''Loads in the blog post using an unique ID. If error, then function returns the error.'''
    postDataResponse = getPostByID(id)
    if (postDataResponse.success):
        data = postDataResponse.payload
        return render_template('post.html', found = True, author = data["author"], title = data["title"], date = data["date"], content = data["content"], edit = data["edit"])
    else:
        return render_template('post.html', found = False, )

@app.route("/createPosts", methods =['GET', 'POST'])
def createPost():
    '''The get function will return the site to create a blog post. The post function will authenticate the user and push the new blog post to the database.'''
    if request.method == "GET":
        return render_template('createPosts.html')
    elif request.method == "POST": #When user submits, the values from the request are taken
        title = request.values['title']
        contents = request.values['contents']

        currentUserResponse = auth.currentUser()

        if currentUserResponse.success:
            userID = dict(currentUserResponse.payload)["username"] #Finds the userID from database
            
            createBlogPostResponse = createBlogPost(title, contents, userID) #Appends values into database.
            
            if createBlogPostResponse.success:
                return redirect("/myBlog")
            else:
                return render_template('createPosts.html') #TODO: Error message
        else:
            return redirect("/login")

@app.route("/logout")
def logout():
    '''Logs currently logged in user out of session.'''
    auth.logout() #function to logout
    return redirect("/") #redirect to login page

if __name__ == "__main__": #false if this file imported as module
    initializeDatabase()
    app.secret_key = urandom(32) # randomized secret key
    #enable debugging, auto-restarting of server when this file is modified
    app.debug = True
    app.run()
