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
import time



class MainHandler(webapp.RequestHandler):
    def get(self):
        render_template(self, 'main.html', {'games': Game.all()})

class AutoVoteHandler(webapp.RequestHandler):
    def post(self):
        gamename = KeyValue.get('current_game')
        if not gamename:
            self.error(500)
            return
        game = Game.get_by_name(gamename)        
        source = game.players.filter('lname =', self.request.get('name').lower()).get()
        if not source:
            source = Player.create(name=self.request.get('name'), game=game)
            source.save()
        target = game.players.filter('lname =', self.request.get('point').lower()).get()
        if not target:
            target = Player.create(name=self.request.get('point'), game=game)
            target.save()
        vote_dt = datetime.datetime.fromtimestamp(int(self.request.get('datetime'))//1000)
        turn = game.turn
        logging.info("Creating vote at %s in game %s on turn %s from %s to %s" % (vote_dt, gamename, turn, source, target))
        Vote.create(vote_dt.date(), vote_dt.time(), turn, source, target, game, "")
        render_template(self, 'votes.json', {"items":game.votes_in_order(), "callback":self.request.get('callback')})

class NewGameHandler(webapp.RequestHandler):
    def post(self, game=""):
        game = Game.create(self.request.get('gamename'))
        self.redirect('/game/'+game.id)

class GameHandler(webapp.RequestHandler):
    def get(self, gamename=""):
        game = Game.get_by_name(gamename)
        if game:
            KeyValue.set('current_game', gamename)
        render_template(self, 'game.html', {"game":game})
    def post(self, game):
        game = Game.get_by_name(game)
        game.turn = self.request.get('turn')
        game.save()
        self.redirect('/game/'+game.id)

class NewVoteHandler(webapp.RequestHandler):
    def post(self, gamename):
        game = Game.get_by_name(gamename)
        source = game.players.filter('name =', self.request.get('source')).get()
        target = game.players.filter('name =', self.request.get('target')).get()
        vote_date = time.strptime(self.request.get('date'),'%Y-%m-%d')
        vote_time = time.strptime(self.request.get('time'), '%H:%M')
        reason = self.request.get('reason')
        turn = self.request.get('turn')
        Vote.create(datetime.date(vote_date.tm_year, vote_date.tm_mon, vote_date.tm_mday), datetime.time(vote_time.tm_hour, vote_time.tm_min), turn, source, target, game, reason)
        self.redirect('/game/'+game.id)
      
class VoteListHandler(webapp.RequestHandler):
    def get(self, gamename=""):
        game = Game.get_by_name(gamename)
        self.response.headers['Content-Type'] = 'application/json'
        render_template(self, 'vote/list.json', {"items":game.votes_in_order(), "callback":self.request.get('callback')})

class EditVoteHandler(webapp.RequestHandler):
    def get(self, gamename="", votekey=""):
        logging.info("Editing vote for game %s and vote %s" % (gamename, votekey))
        game = Game.get_by_name(gamename)
        vote = Vote.get(votekey)
        render_template(self, 'vote/edit.html', {"vote":vote, "game":game})
    def post(self, gamename="", votekey=""):
        game = Game.get_by_name(gamename)
        vote = Vote.get(votekey)
        vote.source = game.players.filter('name =', self.request.get('source')).get()
        vote.target = game.players.filter('name =', self.request.get('target')).get()
        vote_date = time.strptime(self.request.get('date'),'%Y-%m-%d')
        vote_time = time.strptime(self.request.get('time'), '%H:%M:%S')
        vote.reason = self.request.get('reason')
        vote.date = datetime.date(vote_date.tm_year, vote_date.tm_mon, vote_date.tm_mday)
        vote.time = datetime.time(vote_time.tm_hour, vote_time.tm_min)
        vote.save()
        self.redirect("/game/%s" % (gamename))

class DeleteVoteHandler(webapp.RequestHandler):
    def get(self, gamename="", votekey=""):
        game = Game.get_by_name(gamename)
        vote = Vote.get(votekey)
        render_template(self, 'vote/delete.html', {"vote":vote, "game":game})
    def post(self, gamename="", votekey=""):
        game = Game.get_by_name(gamename)
        vote = Vote.get(votekey)
        vote.delete()
        self.redirect('/game/%s' % (gamename))

class NewPlayerHandler(webapp.RequestHandler):
    def post(self, game):
        player = Player.create(name=self.request.get('player'), game=Game.get_by_name(game))
        self.redirect('/game/'+game)

class PlayerListHandler(webapp.RequestHandler):
    def get(self, game="", json=None):
        template = 'player/list.html'
        if json:
            self.response.headers['Content-Type'] = 'application/json'
            template = 'player/list.json'
            
        game = Game.get_by_name(game)
        term = self.request.get('term')
        render_template(self, template, {"items":game.players.filter('name >',term).filter('name <', term+u'\ufffd')})

class EditPlayerHandler(webapp.RequestHandler):
    def get(self, gamename="", votekey=""):
        game = Game.get_by_name(gamename)
        vote = Vote.get(votekey)
        render_template(self, 'voteedit.html', {"vote":vote, "game":game})
    def post(self, gamename="", votekey=""):
        game = Game.get_by_name(gamename)
        vote = Vote.get(votekey)
        vote.source = game.players.filter('name =', self.request.get('source')).get()
        vote.target = game.players.filter('name =', self.request.get('target')).get()
        vote_date = time.strptime(self.request.get('date'),'%Y-%m-%d')
        vote_time = time.strptime(self.request.get('time'), '%H:%M:%S')
        vote.reason = self.request.get('reason')
        vote.date = datetime.date(vote_date.tm_year, vote_date.tm_mon, vote_date.tm_mday)
        vote.time = datetime.time(vote_time.tm_hour, vote_time.tm_min)
        vote.save()
        self.redirect("/game/%s" % (gamename))

class DeletePlayerHandler(webapp.RequestHandler):
    def get(self, gamename="", playerkey=""):
        game = Game.get_by_name(gamename)
        player = Player.get(playerkey)
        render_template(self, 'player/delete.html', {"player":player, "game":game})
    def post(self, gamename="", playerkey=""):
        Player.delete(playerkey)
        self.redirect('/game/%s' % (gamename))



def main():
    application = webapp.WSGIApplication([
    ('/', MainHandler),
    ('/api/vote', AutoVoteHandler),
    
    ('/game/(?P<game>[a-z-_0-9]+)/new', NewGameHandler),
    ('/game/(?P<game>[a-z-_0-9]+)', GameHandler),

    ('/game/(?P<game>[a-z-_0-9]+)/vote/new', NewVoteHandler),
    ('/game/(?P<game>[a-z-_0-9]+)/vote(?P<json>\.json)?', VoteListHandler),
    ('/game/(?P<game>[a-z-_0-9]+)/vote/(?P<votekey>[a-zA-Z-_0-9]+)', EditVoteHandler),
    ('/game/(?P<game>[a-z-_0-9]+)/vote/(?P<votekey>[a-zA-Z-_0-9]+)/delete', DeleteVoteHandler),

    ('/game/(?P<game>[a-z-_0-9]+)/player/new', NewPlayerHandler),
    ('/game/(?P<game>[a-z-_0-9]+)/player(?P<json>\.json)?', PlayerListHandler),
    ('/game/(?P<game>[a-z-_0-9]+)/player/(?P<votekey>[a-zA-Z-_0-9]+)', EditPlayerHandler),
    ('/game/(?P<game>[a-z-_0-9]+)/player/(?P<votekey>[a-zA-Z-_0-9]+)/delete', DeletePlayerHandler),
    ],
                                         debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
