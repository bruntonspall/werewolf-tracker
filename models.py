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
        return self.votes.order('date').order('time')
    def players_by_name(self):
        return self.players.order('lname')

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
        return obj
    @staticmethod
    def delete(key):
        player = Player.get(key)
        db.delete(player.lynch_votes)
        db.delete(player.votes)
        db.delete(player)
        
    def current_votes_against(self):
        turn = self.game.turn
        return self.votes.filter('valid =',True).filter('turn =',self.game.turn).order('time')
#        return Vote.all().filter('target =', self).filter('turn =', self.game.turn).filter('valid =', True).count()
        
    def current_vote(self):
        turn = self.game.turn

        vote = Vote.all().filter('player =', self).filter('turn =', turn).filter('valid = ', True).get()
        if vote:
            return vote
        return None


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
        r = cls.all().filter('k =', key).get()
        if r:
            return r.v
        return default

    @classmethod
    def set(cls, key, value=None):
        r = cls.all().filter('k =', key).get()
        if r:
            r.v = value
            r.save()
            return r
        obj = cls(k=key, v=value)
        obj.save()
        return obj
                