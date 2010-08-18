import os
import datetime
import random
import google.appengine.api.labs.taskqueue 


from google.appengine.ext.webapp import template
from google.appengine.api import memcache
from google.appengine.api import users

import logging
from google.appengine.api.labs.taskqueue.taskqueue import Task
from google.appengine.api.labs import taskqueue


def render_admin_template(self, end_point, template_values):
    user = users.get_current_user()
    if user:
        template_values['greeting'] = ("Welcome, %s! (<a href=\"%s\">sign out</a>)" %
                    (user.nickname(), users.create_logout_url("/admin/")))

    render_template(self, end_point, template_values)

def render_template(self, end_point, template_values):
    path = os.path.join(os.path.dirname(__file__), "templates/" + end_point)
    self.response.out.write(template.render(path, template_values))

def fetch_status_messages_for_list(list_name):
    logging.info('Fetching tweets for "%s"' % list_name)
    feeditemcount = 1
    key = list_name + "_last_status"
    latest_cached = models.get_from_keystore(key)
    original_latest_cached = latest_cached
    list = models.get_list(list_name)
    
    tweets = None;
    status = None;
    
    if list.twitter_list != None :
        #list search
        tweets, status = twitter.get_twitter_list_statuses(list.twitter_user, list.twitter_list, latest_cached)    
    else:
        #user search
        tweets, status = twitter.get_twitter_user_statuses(list.twitter_user, latest_cached)
        
    logging.info('Get %d tweets' % len(tweets))
    tweet_count = 0
    for tweet in tweets:
        if feeditemcount == 1:
            try:
                latest_cached = str(tweet['id'])
            except:
                latest_cached = original_latest_cached
        try:
            tweet_text = tweet['text'].lower()
            if not tweet_text.startswith('@'): #never store replies (ie. starting with @ symbol)
                if '%notags%' in list.tags:
                    logging.info('Found tweet %s without tags' % (tweet))
                    store_tweet(tweet, "%notags%", list.name)
                    tweet_count += 1
                else:
                    for tag in list.tags:
                        if tag.lower() in tweet_text:
                            logging.info('Found tag "%s" in tweet %s' % (tag.lower(),tweet))
                            store_tweet(tweet, tag, list.name)
                            tweet_count += 1
        except:
            logging.error("Failed to store a message")
     
        feeditemcount +=1
    
    if tweet_count > 0:
        models.add_to_keystore(key, latest_cached)
        status = status + " (" + str(tweet_count) + " new tweets)"
    elif status == 'Success':
        status = "Success (no new tweets)"
    return status, tweets, None
        
def markup_message(message, query):
    if "http://" in message.lower():
        messageelements = message.split(" ")
        newmessageelements = []
        for messageelement in messageelements:
            if messageelement[0:7].lower() == "http://":
                newmessageelements.append("<a href='"+ messageelement +"' target='_new'>"+ messageelement +"</a>")
            else:
                newmessageelements.append(messageelement)
        markedupmessage = " ".join(newmessageelements)
    else:
        markedupmessage = message
    if "@" in markedupmessage:
        messageelements = markedupmessage.split(" ")
        newmessageelements = []
        for messageelement in messageelements:
            if messageelement[0:1].lower() == "@":
                if len(messageelement) > 1:
                    newmessageelements.append("<a href='http://twitter.com/"+ messageelement[1: len(messageelement)] +"' target='_new'>"+ messageelement +"</a>")
            else:
                newmessageelements.append(messageelement)
        markedupmessage = " ".join(newmessageelements)
    if "#" in markedupmessage:
        messageelements = markedupmessage.split(" ")
        newmessageelements = []
        for messageelement in messageelements:
            if messageelement[0:1].lower() == "#":
                if len(messageelement) > 1:
                    newmessageelements.append("<a href='http://search.twitter.com/search?q=%23"+ messageelement[1: len(messageelement)] +"'>"+ messageelement +"</a>")
            else:
                newmessageelements.append(messageelement)
        markedupmessage = " ".join(newmessageelements)
    return markedupmessage

def monthname_to_month(monthname):
    month = 1
    if monthname == "Jan":
        month = 1
    if monthname == "Feb":
        month = 2
    if monthname == "Mar":
        month = 3
    if monthname == "Apr":
        month = 4
    if monthname == "May":
        month = 5
    if monthname == "Jun":
        month = 6
    if monthname == "Jul":
        month = 7
    if monthname == "Aug":
        month = 8
    if monthname == "Sep":
        month = 9
    if monthname == "Oct":
        month = 10
    if monthname == "Nov":
        month = 11
    if monthname == "Dec":
        month = 12
    return month

def convert_twitter_datetime(theirdatetime):
    thisdatetime = datetime.datetime(int(theirdatetime[26: 30]), monthname_to_month(theirdatetime[4: 7]), int(theirdatetime[8: 10]), int(theirdatetime[11: 13]), int(theirdatetime[14: 16]), int(theirdatetime[17: 19]))
    return thisdatetime

def queue(queue_name, url):
    logging.log(logging.INFO, "Queue name: " + queue_name)
    taskqueue.Queue(queue_name).add(Task(url=url), transactional=False);