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


from models.posts import BlogPosts
from models.users import Users

from handlers.mainHandler import Handler
from handlers.blogFunctions import NewPost, SinglePost, Delete, Edit
from handlers.commentFunctions import NewComment, EditComment, DeleteComment
from handlers.voteFunctions import Vote, Unvote
from handlers.userFunctions import LogIn, LogOut, SignUp
       


# Class that renders the blog front page
class Blog(Handler):
   def render_front(self,title="",content="",error=""):
      # Helper for deleting all blog posts 
      # if you added a new attribute to the blog posts class
      # posts = BlogPosts.all()
      # for post in posts:
      #   post.delete()
      blog_posts = db.GqlQuery("select * from BlogPosts order by created DESC")
      self.render("blog.html",
                  error=error,
                  blog_posts=blog_posts,
                  user=self.user)
   def get(self):
      self.render_front()



app = webapp2.WSGIApplication([
                             ('/login/?',LogIn),
                             ('/delete/?',Delete),
                             ('/delete-comment/?',DeleteComment),
                             ('/signup/?',SignUp),
                             ('/logout/?',LogOut),
                             ('/comment/([0-9]+)/?',NewComment),
                             ('/?', Blog),
                             (r'/([0-9]+)/?', SinglePost),
                             ('/edit/([0-9]+)/?', Edit),
                             ('/edit-comment/([0-9]+)/?', EditComment),
                             ('/vote/?', Vote),
                             ('/unvote/?', Unvote),
                             ('/newpost/?',NewPost)],debug=True)


# When creating blog posts, input the user into the Posts model
# Figure out what the word for aspect of a database is called
# Row? Column?
# Field!! Holy shit it's field. Glad we found that out
# So yeah, make the user_id a field of the Posts model.
# Whenever we submit a blog, we grab the user_id and put it into the record for that blog

# Is the wording right?
# Fuck i did so bad in databases
# Maybe the word I was thinking of was members?
# Why can't I remember this
# Attribute?




