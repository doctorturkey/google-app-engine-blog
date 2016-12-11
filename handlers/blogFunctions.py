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

from models.comments import Comments
from models.posts import BlogPosts
from models.users import Users

from handlers.mainHandler import Handler


# Class that renders the page for creating a new post
class NewPost(Handler):
  def get(self):
      if not self.user:
        self.redirect("/login")
      else:
        self.render("newpost.html",user = self.user)
  def post(self):
      subject = self.request.get("subject")
      content = self.request.get("content")
      user_id = self.read_secure_cookie("user_id")
      if subject and content and user_id:
        username = Users.get_name(user_id)
        likes = []
        a = BlogPosts(subject = subject, content = content, username= username, likes = likes)
        a.put()
        self.redirect("/"+str(a.key().id()))
      else:
        error = "come on idiot"
        self.render("newpost.html",error=error,title=subject,content=content,user = self.user)

# Class that renders the page of a single blog post
class SinglePost(Handler):
  def get(self,post_id):
    post = BlogPosts.get_by_id(int(post_id))
    if not post:
      print "Uh oh"
    self.render("single_blog.html",blog=post,user = self.user)

# Handler for deleting a post, post_id to be deleted is passed through ajax as json
class Delete(Handler):
  def post(self):
    data = json.loads(self.request.body)

    # data.post.delete()
    post_id = int(data['post'])
    post = BlogPosts.get_by_id(post_id)
    

    if post:
      if self.user.username == post.username:
         post.delete()
    self.redirect("/")

# TODO: Sending post_id as a cookie that is secure.

# The class that allows for users to edit their posts
class Edit(Handler):
  def get(self,post_id):
      # Grabs the post_id from the url, then populates the page with the users data to edit
      post = BlogPosts.get_by_id(int(post_id))
      self.render("editpost.html",subject=post.subject,content=post.content,id=post_id,user = self.user)
  def post(self,post_id):
      # Checks to make sure that the correct user is editing the data, and that they have the required fields
      subject = self.request.get("subject")
      content = self.request.get("content")
      post_id = self.request.get("id")
      user_id = self.read_secure_cookie("user_id")
      if subject and content and user_id and post_id:
        p = BlogPosts.get_by_id(int(post_id))
        username = Users.get_name(int(user_id))
        if p.username == username:
          p.subject = subject
          p.content = content
          p.put()
          self.redirect("/"+str(p.key().id()))
      else:
        error = "come on idiot"
        self.render("editpost.html",error=error,id=post_id,subject=subject,content=content,user = self.user)

