from flask import request, render_template, Flask, jsonify, redirect, Response
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import requests
import re
import json
import slack
import os
from pathlib import Path
from slackeventsapi import SlackEventAdapter

app = Flask(__name__)

#Replace this with your data base config
app.config['SQLALCHEMY_DATABASE_URI'] = "xxxxxxxxx"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
db.init_app(app)

#Replace with User OAuth Token
client = slack.WebClient(token="xxxxxxx")

class Rose(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(100), nullable=False)
    number_of_roses = db.Column(db.Integer, nullable=False)

    def __init__(self, user, number_of_roses):
        self.user = user
        self.number_of_roses = number_of_roses

# for command bots
@app.route('/rose', methods=['POST'])
def roses():
    data = request.form
    channel_id = data.get('channel_id')
    user_id = data.get('user_id')
    arg = data.get('text').split()

    if arg == []:
        client.chat_postMessage(channel=channel_id, text = "invalid number of arguments, try again bud." ) 
        return Response(), 200
    
    for user in client.users_list()["members"]:
        if user["name"] ==  arg[0][1:] and not user['is_bot']:
            results = Rose.query.filter_by(user=user["id"]).first()
            roses = 1
            the_rose = ":rose:"
            if results == None: 
                entry = Rose(user["id"], 1)
                db.session.add(entry)
                db.session.commit()
            else:
                roses = int(results.number_of_roses)
                if arg[-1] == "🥀" or arg[-1]== ":wilted_flower:":
                    roses = int(results.number_of_roses)-1
                    if roses < 0: 
                        roses = 0
                    the_rose = ":wilted_flower:"
                else:
                    roses = int(results.number_of_roses)+1
                results.number_of_roses = roses
                db.session.merge(results)
                db.session.commit()
            reciever = "<@" + user["id"] +">"
            giver = " <@" + user_id + ">"
            client.chat_postMessage(channel=channel_id, text = reciever + " has recived a " + the_rose + " from " + giver + ". Now " + reciever + " has " + str(roses) + " in their garden") 
            return Response(), 200
        elif arg[0][1:] == "rose_garden":
            client.chat_postMessage(channel=channel_id, text = "the garden cat is so greatful for your rose." ) 
            return Response(), 200
    results = Rose.query.filter_by(user=user_id).first()
    roses = int(results.number_of_roses)-1
    results.number_of_roses = roses
    db.session.merge(results)
    db.session.commit()
    client.chat_postMessage(channel=channel_id, text =  arg[0] + " is not a valid user, garden cat is removing a rose from your garden for testing its inteligence" )
    return Response(), 200            


@app.route('/garden', methods=['POST'])
def garden():
    data = request.form
    channel_id = data.get('channel_id')
    user_id = data.get('user_id')
    arg = data.get('text').split()

    if arg != []:
        client.chat_postMessage(channel=channel_id, text = "invalid number of arguments, try again bud." ) 
        return Response(), 200
    else:
        results = Rose.query.filter_by(user=user_id).first()
        garden = ":rose:" * int(results.number_of_roses)
        client.chat_postMessage(channel=channel_id, text = "<@" + user_id +">'s garden: " + garden)
        return Response(), 200

if __name__ == '__main__':  
    app.run()