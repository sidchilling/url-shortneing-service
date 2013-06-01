import handlers
import webapp2

app = webapp2.WSGIApplication([
    ('/get_user_details', handlers.UserDetails),
    ('/get_short_url', handlers.GetShortURL),
    ('/r/([^/]+)', handlers.Redirect),
    ('/', handlers.MainPage),
    ], debug = True)
