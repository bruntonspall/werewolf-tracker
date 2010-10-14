#!/usr/bin/env python
# encoding: utf-8
"""
models.py

Created by MBS on 2010-08-13.
Copyright (c) 2010 __MyCompanyName__. All rights reserved.
"""
from google.appengine.api import memcache
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.ext.db import djangoforms

import random
import datetime
import time
import logging

import helpers

def slugify(word):
    return word.replace(' ', "-").lower()

def cached(name, f, *args, **kwargs):
    result = memcache.get(name)
    if not result:
        logging.info('CACHE MISS for %s' % name)
        result = f(name, *args, **kwargs)
    else:
        logging.info('CACHE HIT for %s' % name)
    if result:
        memcache.set(name, result, 60)
    return result

class Game(db.Model):
    id = db.StringProperty(required=True)
    name = db.StringProperty(required=True)
    turn = db.StringProperty(required=False)
    
    @staticmethod
    def get_by_name(name):
        return Game.all().filter('id =', name).get()

    @staticmethod
    def create(name):
        game = Game(name=name, id=slugify(name))
        game.turn = "day 1"
        game.save()
        return game

    def votes_in_order(self):
        key = "votes_in_order:%s:%s" % (self.turn, self.id)
        results = cached(key, lambda key,self: self.votes.filter('turn =', self.turn).order('date').order('time'), self)
        logging.info('Got results: %s' % results)
        return results

    def players_by_name(self):
        key = "players_by_name:%s:%s" % (self.turn, self.id)
        players = cached(key, lambda key,self: self.players.order('lname'), self)
        return players

    def fix_up(self, turn):
        for vote in self.votes_in_order():
            #Find replacement votes
            other_votes = self.votes.filter('turn =', turn).filter('valid =', True).filter('source =', vote.source).order('date').order('time')
            if other_votes.count() > 1:
                for v in other_votes:
                    v.valid = False
                    v.save()
                v.valid = True
                v.save()

class Player(db.Model):
    name = db.StringProperty(required=True)
    lname = db.StringProperty(required=True)
    role = db.StringProperty(required=False)
    allegiance = db.StringProperty(required=False)
    status = db.StringProperty(required=False)
    game = db.ReferenceProperty(Game, collection_name="players")

    @staticmethod
    def create(name, game):
        obj = Player(name=name, lname=name.lower(), game=game)
        obj.save()
        memcache.delete("players_by_name:%s:%s" % (game.turn, game.key()))
        return obj

    @staticmethod
    def delete(key):
        player = Player.get(key)
        db.delete(player.lynch_votes)
        db.delete(player.votes)
        db.delete(player)
        
    def current_votes_against(self):
        key = "votes_against:%s:%s" % (self.game.turn, self.lname)
        return cached(key, lambda key,self: self.votes.filter('valid =',True).filter('turn =',self.game.turn).order('date').order('time'), self)
        
    def current_vote(self):
        key = "vote:%s:%s" % (self.game.turn, self.lname)
        return cached(key, lambda key,self: Vote.all().filter('player =', self).filter('turn =', self.game.turn).filter('valid = ', True).get(), self)


class Vote(db.Model):
    date = db.DateProperty(required=True)
    time = db.TimeProperty(required=True)
    turn = db.StringProperty(required=True)
    source = db.ReferenceProperty(Player, collection_name="lynch_votes", required=True)
    target = db.ReferenceProperty(Player, collection_name="votes", required=True)
    game = db.ReferenceProperty(Game, collection_name="votes", required=True)
    valid = db.BooleanProperty(required=True, default=True)
    reason = db.StringProperty(required=False)
    @staticmethod
    def create(date, time, turn, source, target, game, reason=""):
        oldvote = Vote.all().filter('source =', source).filter('turn =', turn).filter('game =',game).get()
        if oldvote:
            oldvote.valid = False
            oldvote.save()
        obj = Vote(date=date, time=time, turn=turn, source=source, target=target, game=game, reason=reason, valid=True)
        obj.save()
        return obj


class KeyValue(db.Model):
    k = db.StringProperty(required=True)
    v = db.StringProperty(required=True)
    
    @classmethod
    def get(cls, key, default=None):
        r = cached(key, lambda k,cls: cls.all().filter('k =', k).get(), cls)
        if r:
            return r.v
        return default

    @classmethod
    def set(cls, key, value=None):
        r = cls.all().filter('k =', key).get()
        if r:
            r.v = value
        else:
            r = cls(k=key, v=value)
        r.save()
        memcache.set(key, r)
        return r
                
