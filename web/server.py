#!/usr/bin/env python
"""A simple example of connecting to Earth Engine using App Engine."""



# Works in the local development environment and when deployed.
# If successful, shows a single web page with the SRTM DEM
# displayed in a Google Map.  See accompanying README file for
# instructions on how to set up authentication.

import os
import datetime
from datetime import timedelta

import oauth2client
import oauth2client.client

import jinja2
import webapp2

import config_web

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))


class MainPage(webapp2.RequestHandler):
  def get(self):                             # pylint: disable=g-bad-name
    """Request an image from Earth Engine and render it to a web page."""

    expire_time = datetime.datetime.now() + timedelta(seconds=config_web.EE_TOKEN_EXPIRE_IN_SEC)
    
    config_web.EE_ACCESS_TOKEN = oauth2client.client.OAuth2Credentials(
        None, config_web.EE_CLIENT_ID, config_web.EE_CLIENT_SECRET, config_web.EE_REFRESH_TOKEN,
        expire_time, 'https://accounts.google.com/o/oauth2/token', None).get_access_token().access_token

    template_values = {
        'client_id': config_web.EE_CLIENT_ID,
        'token_type': config_web.EE_TOKEN_TYPE,
        'access_token': config_web.EE_ACCESS_TOKEN,
        'token_expires_in_sec': config_web.EE_TOKEN_EXPIRE_IN_SEC,
        'token_expire_time': expire_time.strftime("%A, %d. %B %Y %I:%M%p:%S")
    }

    template = jinja_environment.get_template('index.html')

    self.response.out.write(template.render(template_values))


class RefreshAccessToken(webapp2.RequestHandler):
  def post(self):
    self.redirect('/')

app = webapp2.WSGIApplication([('/', MainPage)], debug=True)
