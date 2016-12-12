from google.appengine.ext import db
import sys
import helpers
# Datastore class for our users
class Users(db.Model):
  username = db.StringProperty(required=True)
  password = db.TextProperty(required=True)
  email = db.StringProperty()

  # Some helpful classes for our Users class

  @classmethod
  def by_id(cls, uid):
      return Users.get_by_id(uid)

  @classmethod
  def by_name(cls, username):
      u = db.GqlQuery("select * from Users where username=:1",
                      username).get()
      return u
  @classmethod
  def get_name(cls, user_id):
      u = Users.get_by_id(int(user_id))
      return u.username
  @classmethod
  def register(cls, name, pw):
      pw_hash = helpers.make_pw_hash(name, pw)
      return Users(username = name,
                  password = pw_hash)

  @classmethod
  def login(cls, name, pw):
      u = cls.by_name(name)
      if u and helpers.valid_pw(name, pw, u.password):
          return u

