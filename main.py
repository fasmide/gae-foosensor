#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import models
import jinja2
import logging
import os
import json

from google.appengine.api import channel

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

global lastState
lastState = "off"


class MainHandler(webapp2.RequestHandler):
    def get(self):
        client = models.Client()
        client.put()
        token = channel.create_channel(str(client.key()))
        global lastState
        template_values = {'token': token, 'lastState': lastState}

        template = jinja_environment.get_template('index.html')
        self.response.out.write(template.render(template_values))


class ConnectedHandler(webapp2.RequestHandler):
    def post(self):
        #Does nothing
        logging.info("Someone connected: " + self.request.get('from'))


class DisconnectedHandler(webapp2.RequestHandler):
    def post(self):
        client = models.Client.get(self.request.get('from'))
        client.delete()


class SensorHandler(webapp2.RequestHandler):
    #do not push this button ;)
    def post(self):
        state = self.request.get('value')

        if not state:
            logging.info("Someone sent a request without a state")
            return

        if state not in ('on', 'off'):
            logging.info("Someone sent something else then on or off")
            return

        global lastState
        lastState = state
        logging.info("Good sensor state: " + state)

        clients = models.Client.all()
        for client in clients:
            channel.send_message(str(client.key()), json.dumps({'state': state}))


app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/_ah/channel/connected/', ConnectedHandler),
    ('/_ah/channel/disconnected/', DisconnectedHandler),
    ('/sensorState', SensorHandler)
], debug=True)
