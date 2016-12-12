from google.appengine.ext import db
import sys
import helpers
import handlers.mainHandler as blog
#from comments import Comments

# The datastore class for our blog posts
class BlogPosts(db.Model):
  subject = db.StringProperty(required=True)
  content = db.TextProperty(required=True)
  created = db.DateTimeProperty(auto_now_add = True)
  username = db.TextProperty(required=True)
  last_modified = db.DateTimeProperty(auto_now = True)
  likes = db.ListProperty(str)

  def render(self,user):
      # allows for users to do new lines in their blog posts
      self._render_text = self.content.replace('\n', '<br>') 
      comments = db.GqlQuery("select * from Comments where post_id = :1",
                             self.key().id())
      return blog.render_str("post.html", 
                              p=self, 
                              user=user,
                              comments=comments)
