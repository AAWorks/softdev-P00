import sqlite3   #enable control of an sqlite database
from utils.response import Response

DB_FILE="database.db"

db = sqlite3.connect(DB_FILE, check_same_thread=False) #open if file exists, otherwise create
c = db.cursor()               #facilitate db ops -- you will use cursor to trigger db events

def initializeUsersTable():
    c.execute('''CREATE TABLE IF NOT EXISTS users(
    ID INTEGER PRIMARY KEY,
    username TEXT,
    displayName TEXT,
    password TEXT,
    UNIQUE (username, ID))''')

def initializePostsTable():
    c.execute('''CREATE TABLE IF NOT EXISTS blogs(
    ID INTEGER PRIMARY KEY,
    author TEXT,
    date TEXT,
    title TEXT,
    content TEXT,
    edit TEXT,
    UNIQUE (ID))''')

def initializeDatabase():
    initializeUsersTable()
    initializePostsTable()

# AUTH
def addUser(username, displayName, password):
    try:
        c.execute("INSERT INTO users (username, displayName, password) VALUES(? , ?, ?)", (username, displayName, password))
        db.commit()
    except Exception as err:
        return Response(False, None, err)

def getUserByUsername(username):
    try:
        c.execute("SELECT * FROM users WHERE username = ?", (username,))
        data = c.fetchone()

        res = {"id": data[0], "username": data[1], "displayName": data[2], "password": data[3],}

        return Response(True, res, "")
    except Exception as err:
        return Response(False, None, err)

# BLOG MANAGEMENT

def search(searchQuery):
    q = "%"+searchQuery+"%"
    c.execute("SELECT * FROM blogs WHERE title LIKE ? OR author LIKE ? ORDER by date DESC", (q, q))
    data = c.fetchall()
    return data

def pullUserData(userID):
    c.execute("SELECT * FROM blogs WHERE author IS ? ORDER by date DESC", (userID,))
    data = c.fetchall()
    return data

def createBlogPost(title, content, userID):
    c.execute("INSERT INTO blogs (author, date, title, content, edit) VALUES (:userID, (SELECT DATETIME('now')), :title, :content, (SELECT DATETIME('now')))", {'userID': userID, 'title': title, 'content': content})
    db.commit()

def loadHomePage():
    c.execute("SELECT * FROM blogs ORDER BY date DESC")
    data = c.fetchall()
    return data

def editBlogPost(id, title, content, userID):
    c.execute("UPDATE blogs SET title =?, content =?, edit = (SELECT DATETIME('now')) WHERE id = ?", (title, content, id))
    db.commit()

def getPostByID(id):
    try:
        c.execute("SELECT * FROM blogs WHERE id = ?", (id,))
        data = c.fetchone()

        res = {"id": data[0], "author": data[1], "date": data[2], "title": data[3], "content": data[4], "edit": data[5]}

        return Response(True, res, "")
    except Exception as err:
        return Response(False, None, err)

def loadEdit(id):
    c.execute("SELECT * FROM blogs WHERE id is ?", (id))
    data = c.fetchone()
    return data

def deleteBlogPost(id):
    try:
        c.execute("DELETE FROM blogs WHERE id is ?", (id))
        db.commit()

        return Response(True, None, "")
    except Exception as err:
        return Response(False, None, err)
