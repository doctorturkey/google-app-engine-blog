import os
import re
import webapp2
import jinja2
from google.appengine.ext import db
import random
import string
import hashlib
import hmac
import json
import helpers
from handlers.mainHandler import Handler

from models.comments import Comments
from models.posts import BlogPosts
from models.users import Users


# Class for signing users up
class SignUp(Handler):
  def get(self):
    # Helpful for clearing out the users when new attributes are added
    # users = Users.all()
    # for user in users:
    #   user.delete()
    self.render("signup.html")
  def post(self):
    errorUsername=""
    errorPassword=""
    errorNoMatch=""
    errorEmail=""
    username=""
    email=""
    username = self.request.get('username')
    errorFlag=True
    if not username:
        username=""

    password = self.request.get('password')
    if not password:
        password=""

    verify = self.request.get('verify')
    if not verify:
        verify=""

    email = self.request.get('email')
    if not email:
        email=""

    if not helpers.verify_username(username):
        errorUsername="Please submit a valid username"
        errorFlag = False
    if not helpers.verify_password(password):
        errorPassword="Please enter a valid password"
        errorFlag = False
    if password != verify:
        errorNoMatch="Please make the passwords match"
        errorFlag = False
    if not helpers.verify_email(email):
        errorEmail="Please enter a valid email"
        errorFlag = False
    if not errorFlag:
      print "There was an error"
      self.render('signup.html',
                         errorUsername=errorUsername,
                         errorPassword=errorPassword,
                         errorNoMatch=errorNoMatch,
                         errorEmail=errorEmail,
                         username=username,
                         email=email)
    else:
      u = Users.by_name(username)
      if u:
        self.render('signup.html',errorUsername="That's already Taken")
      else:
        user = Users.register(username,password)
        user.put()
        self.login(user)
        self.redirect('/')

# Handler for logging users in
class LogIn(Handler):
  def get(self):
    self.render("login.html")
  def post(self):
    username = self.request.get('username')
    password = self.request.get('password')
    if not username and password:
      self.render('login.html',errorMessage="Try again idiot")
    user = Users.login(username,password)
    if not user:
      self.render("login.html",errorUsername="Username/Password does not match")
    else:
      self.response.headers['Content-Type'] = 'text/plain'
      self.login(user)
      self.redirect('/')

# A very simple handler that just clears the cookie and redirects to the home page
class LogOut(Handler):
  def get(self):
    self.response.headers['Content-Type'] = 'text/plain'
    self.logout()
    self.redirect("/")


