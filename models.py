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

class Player(db.Model):
    name = db.StringProperty(required=True)
    role = db.StringProperty(required=False)
    allegiance = db.StringProperty(required=False)
    game = db.ReferenceProperty(Game, collection_name="players")
    @staticmethod
    def create(name, game):
        obj = Player(name=name, game=game)
        obj.save()
        return obj

class Vote(db.Model):
    date = db.DateProperty(required=True)
    time = db.TimeProperty(required=True)
    turn = db.StringProperty(required=True)
    source = db.ReferenceProperty(Player, collection_name="lynch_votes", required=True)
    target = db.ReferenceProperty(Player, collection_name="votes", required=True)
    game = db.ReferenceProperty(Game, collection_name="votes", required=True)
    reason = db.StringProperty(required=False)
    @staticmethod
    def create(date, time, turn, source, target, game, reason=""):
        obj = Vote(date=date, time=time, turn=turn, source=source, target=target, game=game, reason=reason)
        obj.save()
        return obj
