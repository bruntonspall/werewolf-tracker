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
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from helpers import *
from models import *
import logging


class MainHandler(webapp.RequestHandler):
    def get(self):
        render_template(self, 'main.html', {'games': Game.all()})

class VoteHandler(webapp.RequestHandler):
    def get(self, game):
        render_template(self, 'votes.html', {'game':Game.get_by_name(game)})
    def post(self):
        logging.info("source:"+self.request.get('source'))
        logging.info("target:"+self.request.get('target'))
        logging.info("datetime:"+self.request.get('datetime'))
        pass

class GameHandler(webapp.RequestHandler):
    def get(self, game=""):
        game = Game.get_by_name(game)
        render_template(self, 'game.html', {"game":game})
    def post(self, game=""):
        game = Game.create(self.request.get('gamename'))
        self.redirect('/game/'+game.id)

class PlayerHandler(webapp.RequestHandler):
    def post(self, game):
        player = Player.create(name=self.request.get('player'), game=Game.get_by_name(game))
        self.redirect('/game/'+game)

class PlayerJsonHandler(webapp.RequestHandler):
    def get(self, game=""):
        self.response.headers['Content-Type'] = 'application/json'
        game = Game.get_by_name(game)
        term = self.request.get('term')
        render_template(self, 'players.json', {"players":game.players.filter('name >',term).filter('name <', term+u'\ufffd')})




def main():
    application = webapp.WSGIApplication([
    ('/', MainHandler),
    ('/game/(?P<game>[a-z-_0-9]+)/vote', VoteHandler),
    ('/game(?:/(?P<game>[a-z-_0-9]+))?', GameHandler),
    ('/game/(?P<game>[a-z-_0-9]+)/players', PlayerHandler),
    ('/game/(?P<game>[a-z-_0-9]+)/players/json', PlayerJsonHandler),
    ],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
