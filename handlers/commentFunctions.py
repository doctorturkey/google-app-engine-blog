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

# Handler for making a new comment
class NewComment(Handler):
  def get(self,post_id):

      if not self.user:
        self.redirect("/login")
      else:
        self.render("newcomment.html",user = self.user,post_id=post_id)
  def post(self,post_id):
      content = self.request.get("content")
      user_id = self.read_secure_cookie("user_id")
      if content and user_id:
        username = Users.get_name(user_id)
        a = Comments(content = content,username= username, post_id=int(post_id))
        a.put()
        self.redirect("/")
      else:
        error = "come on idiot"
        self.render("newcomment.html",error=error,content=content,user = self.user)

 # Handler for editing a comment. Similar rules as the other editor classes
class EditComment(Handler):
  def get(self,comment_id):
      comment = Comments.get_by_id(int(comment_id))
      if comment:
         if comment.username == self.user.username:
            self.render("newcomment.html",content = comment.content)
         else:
            self.redirect("/")
      else:
         self.redirect("/")
  def post(self,comment_id):
      content = self.request.get("content")
      user_id = self.read_secure_cookie("user_id")
      if content and user_id:
        a = Comments.get_by_id(int(comment_id))
        if a:
           if a.username == self.user.username:
              a.content = content
              a.put()
              self.redirect("/")
        else:
           error = "that comment doesn't exist"
           self.render("newcomment.html",error=error,content=content)
      else:
        error = "come on idiot"
        self.render("newcomment.html",error=error,content=content)


# Handler for deleting a comment. Similar in design to deleting a post
class DeleteComment(Handler):
  def post(self):
    data = json.loads(self.request.body)
    # data.post.delete()
    comment_id = int(data['comment'])
    comment = Comments.get_by_id(comment_id)
    if comment:
      if self.user.username == comment.username:
        comment.delete()
    self.redirect("/")

