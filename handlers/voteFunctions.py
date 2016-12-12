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


# Handler for upvoting something
# adds the current user to the list of users that like the post
# This was in the hopes of someday 
# incorporating a "Users who likes this:" feature
class Vote(Handler):
  def post(self):
    data = json.loads(self.request.body)
    post_id = int(data['id'])
    likes_test = data['likes']
    user = Users.get_name(self.read_secure_cookie("user_id"))
    post = BlogPosts.get_by_id(post_id)
    if post.username != user and user not in post.likes:
        post.likes.append(user)
        post.put()

# Handler for taking away a vote
# Similar in design to the upvoting
class Unvote(Handler):
  def post(self):
    data = json.loads(self.request.body)
    post_id = int(data['id'])
    likes_test = data['likes']
    user = Users.get_name(self.read_secure_cookie("user_id"))
    post = BlogPosts.get_by_id(post_id)
    if user in post.likes and post.username!=user:
        post.likes.remove(user)
        post.put()
