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

SECRET = "hello there"

# Makes a salt of 5 letters made for each password
def make_salt():
  return ''.join(random.choice(string.letters) for x in xrange(5))

# Makes an hmac hex string based on the secret
def hash_str(s):
    return hmac.new(SECRET,s).hexdigest()

# Makes a string for the user cookie based on the hmac hex string
def make_secure_val(s):
    return "%s|%s" % (s, hash_str(s))

# Makes a secure sha256 password based on the salt, either making a new one
# or using the old one from the end of the stored password
def make_pw_hash(name, pw, salt = None):
  if not salt:
    salt = make_salt()
  h = hashlib.sha256(name+pw+salt).hexdigest()
  return "%s,%s" % (h, salt)

# Makes sure the password is valid for the user by checking
# the hashes of the stored password hash with the hash made
# from the newly provided information
def valid_pw(name, pw, h):
  salt = h.split(',')[1]
  return h == make_pw_hash(name, pw, salt)

# check to make sure the user_id cookie has the correct hash
def check_secure_val(h):
    splitting = h.split('|')
    if len(splitting) >1:
        if hash_str(splitting[0])==splitting[1]:
            return splitting[0]
    return None


username_check = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
# checks a valid password
password_check = re.compile(r"^.{3,20}$")
# checks for a valid password, 
# though with HTML5 we can use the type="email" attribute to render this obsolete
email_check    = re.compile(r"^[\S]+@[\S]+.[\S]+$")

# functions for the returning the regex matches above
def verify_email(email):
   if email!="":
       return email_check.match(email)
   else:
       return True

def verify_password(password):
    return password_check.match(password)

def verify_username(username):
    return username_check.match(username)
