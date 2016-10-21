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

SECRET = "fuckyou"

def make_salt():
  return ''.join(random.choice(string.letters) for x in xrange(5))

def hash_str(s):
    return hmac.new(SECRET,s).hexdigest()

def make_secure_val(s):
    return "%s|%s" % (s, hash_str(s))


def make_pw_hash(name, pw, salt = None):
  if not salt:
    salt = make_salt()
  h = hashlib.sha256(name+pw+salt).hexdigest()
  return "%s,%s" % (h, salt)

def valid_pw(name, pw, h):
  salt = h.split(',')[1]
  return h == make_pw_hash(name, pw, salt)

def check_secure_val(h):
    splitting = h.split('|')
    if len(splitting) >1:
        if hash_str(splitting[0])==splitting[1]:
            return splitting[0]
    return None

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),autoescape=True)
username_check = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
password_check = re.compile(r"^.{3,20}$")
email_check    = re.compile(r"^[\S]+@[\S]+.[\S]+$")

def verify_email(email):
   if email!="":
       return email_check.match(email)
   else:
   	   return True

def verify_password(password):
    return password_check.match(password)

def verify_username(username):
    return username_check.match(username)

def render_str(template, **params):
    t = jinja_env.get_template(template)
    return t.render(params)


class Handler(webapp2.RequestHandler):
   def write(self, *a, **kw):
      self.response.out.write(*a, **kw)
   def render_str(self,template, **params):
   	  return render_str(template,**params)

   def render(self,template, **kw):
   	  self.write(self.render_str(template,**kw))

   def set_secure_cookie(self,name,val):
      cookie_val = make_secure_val(val)
      self.response.headers.add_header(
        'Set-Cookie',
        '%s=%s; Path=/' % (name, cookie_val))
   def read_secure_cookie(self, name):
      cookie_val = self.request.cookies.get(name)
      return cookie_val and check_secure_val(cookie_val)
   def login(self, user):
      self.set_secure_cookie('user_id',str(user.key().id()))
   def logout(self):
      self.response.headers.add_header('Set-Cookie', 'user_id=; Path/')

   def initialize(self, *a, **kw):
      webapp2.RequestHandler.initialize(self, *a, **kw)
      uid = self.read_secure_cookie("user_id")
      self.user = uid and Users.by_id(int(uid))


class BlogPosts(db.Model):
  subject = db.StringProperty(required=True)
  content = db.TextProperty(required=True)
  created = db.DateTimeProperty(auto_now_add = True)
  username = db.TextProperty(required=True)
  last_modified = db.DateTimeProperty(auto_now = True)
  likes = db.ListProperty(str)

  def render(self,user):
      self._render_text = self.content.replace('\n', '<br>')
      comments = db.GqlQuery("select * from Comments where post_id = :1",self.key().id())
      return render_str("post.html", p = self, user = user,comments =comments)



class Blog(Handler):
   def render_front(self,title="",content="",error=""):
      # posts = BlogPosts.all()
      # for post in posts:
      #   post.delete()
      blog_posts = db.GqlQuery("select * from BlogPosts order by created DESC")
      self.render("blog.html",error=error,blog_posts = blog_posts,user = self.user)
      # self.render("blog.html",title=title,content=content,error=error)
   def get(self):
      self.render_front()

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
        a = BlogPosts(subject = subject, content = content,username= username, likes = likes)
        a.put()
        self.redirect("/"+str(a.key().id()))
      else:
        error = "come on idiot"
        self.render("newpost.html",error=error,title=subject,content=content,user = self.user)

class SinglePost(Handler):
  def get(self,post_id):
    post = BlogPosts.get_by_id(int(post_id))
    if not post:
      print "Uh oh"
    self.render("single_blog.html",blog=post,user = self.user)


class Users(db.Model):
  username = db.StringProperty(required=True)
  password = db.TextProperty(required=True)
  @classmethod
  def by_id(cls, uid):
      return Users.get_by_id(uid)

  @classmethod
  def by_name(cls, username):
      u = db.GqlQuery("select * from Users where username=:1",username).get()
      return u
  @classmethod
  def get_name(cls, user_id):
      u = Users.get_by_id(int(user_id))
      return u.username
  @classmethod
  def register(cls, name, pw):
      pw_hash = make_pw_hash(name, pw)
      return Users(username = name,
                  password = pw_hash)

  @classmethod
  def login(cls, name, pw):
      u = cls.by_name(name)
      if u and valid_pw(name, pw, u.password):
          return u

class Comments(db.Model):
  content = db.TextProperty(required=True)
  post_id = db.IntegerProperty(required=True)
  username = db.StringProperty(required=True)
  created = db.DateTimeProperty(auto_now_add = True)
  last_modified = db.DateTimeProperty(auto_now = True)
  def render(self,user):
     self._render_text = self.content.replace('\n', '<br>')
     return render_str('comment.html',c = self, user = user)

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

class EditComment(Handler):
  def get(self,comment_id):
      comment = Comments.get_by_id(int(comment_id))
      self.render("newcomment.html",content = comment.content)
  def post(self,comment_id):
      content = self.request.get("content")
      user_id = self.read_secure_cookie("user_id")
      if content and user_id:
        a = Comments.get_by_id(int(comment_id))
        a.content = content
        a.put()
        self.redirect("/")
      else:
        error = "come on idiot"
        self.render("newcomment.html",error=error,content=content)

class Delete(Handler):
  def post(self):
    data = json.loads(self.request.body)
    # data.post.delete()
    post_id = int(data['post'])
    BlogPosts.get_by_id(post_id).delete()
    self.redirect("/")

class DeleteComment(Handler):
  def post(self):
    data = json.loads(self.request.body)
    # data.post.delete()
    comment_id = int(data['comment'])
    Comments.get_by_id(comment_id).delete()
    self.redirect("/")

class Vote(Handler):
  def post(self):
    data = json.loads(self.request.body)
    post_id = int(data['id'])
    likes_test = data['likes']
    user = Users.get_name(self.read_secure_cookie("user_id"))
    post = BlogPosts.get_by_id(post_id)
    post.likes.append(user)
    post.put()

class Unvote(Handler):
  def post(self):
    data = json.loads(self.request.body)
    post_id = int(data['id'])
    likes_test = data['likes']
    user = Users.get_name(self.read_secure_cookie("user_id"))
    post = BlogPosts.get_by_id(post_id)
    post.likes.remove(user)
    post.put()


# TODO: Sending post_id as a cookie that is secure.

class Edit(Handler):
  def get(self,post_id):
      post = BlogPosts.get_by_id(int(post_id))
      self.render("editpost.html",subject=post.subject,content=post.content,id=post_id,user = self.user)
  def post(self,post_id):
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

class SignUp(Handler):
  def get(self):
    # users = Users.all()
    # for user in users:
    #   user.delete()
    print Users.all().count()
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

    if not verify_username(username):
        errorUsername="Please submit a valid username"
        errorFlag = False
    if not verify_password(password):
        errorPassword="Please enter a valid password"
        errorFlag = False
    if password != verify:
        errorNoMatch="Please make the passwords match"
        errorFlag = False
    if not verify_email(email):
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


class LogOut(Handler):
  def get(self):
    self.response.headers['Content-Type'] = 'text/plain'
    self.logout()
    self.redirect("/")

class Welcome(Handler):
  def get(self):
    user_id=self.read_secure_cookie('user_id')
    if user_id:
        # key = db.Key.from_path('Users',int(user_id))
        # username = db.get(key)
        user = Users.get_by_id(int(user_id))
        self.render('welcome.html',username=user.username)
    else:
      self.redirect('/signup')
      


app = webapp2.WSGIApplication([
                             ('/login',LogIn),
                             ('/delete',Delete),
                             ('/delete-comment',DeleteComment),
                             ('/signup',SignUp),
                             ('/logout',LogOut),
                             ('/welcome',Welcome),
                             ('/comment/([0-9]+)',NewComment),
                             ('/?', Blog),
                             (r'/([0-9]+)', SinglePost),
                             ('/edit/([0-9]+)', Edit),
                             ('/edit-comment/([0-9]+)', EditComment),
                             ('/vote', Vote),
                             ('/unvote', Unvote),
                             ('/newpost',NewPost)],debug=True)


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




