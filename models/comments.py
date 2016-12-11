from google.appengine.ext import db
import sys
import handlers.mainHandler as blog

# The datastore class for our Comments
# Comments have a post_id property which
# corresponds to the post that that comment was meant for
class Comments(db.Model):
  content = db.TextProperty(required=True)
  post_id = db.IntegerProperty(required=True)
  username = db.StringProperty(required=True)
  created = db.DateTimeProperty(auto_now_add = True)
  last_modified = db.DateTimeProperty(auto_now = True)
  def render(self,user):
     self._render_text = self.content.replace('\n', '<br>')
     return blog.render_str('comment.html',c = self, user = user)
