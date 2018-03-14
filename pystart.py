# -*- coding: utf-8 -*-
from chatterbot import ChatBot
import json
import sqlite3 as sq
from pymessenger.bot import Bot
from pymessenger import Element, Button
from training import pytraining
from flask import Flask, redirect, url_for, request
app = Flask(__name__)



#Get access token 
def get_access_token(page):
    if page.upper() == "PYTHONWORKSHOPS":
        token = "EAAbTWtBx3EEBAPICjzhEI3fuZB2BjvZBEpZArTq8XZAwnnFeI5BqFYPTT8TgJpaLEYOGs8L0NHE1ZALwZCoK4PnGyBCRl0ULBq9Ygw4IjCxZCneYNsV3kQLZApummj4y054rpTZCEySxLAZCuqHhymfMAqMzi9LqSMGxVRsfOLwExx1QZDZD"
    elif page.upper() == "ESCHOOL":
        token = "EAAbTWtBx3EEBAIxRbuQOkZAsFQJI6yCU0gdUcZApdhgVJN22eJvPVJbdlLcwmf1WwEwdZCnAXTHdtCbJfmIpKPAoafIxahgjy0ZCYbbbwbsvAdBBBlflljiSX00U3DI5Pzr4pQyVE3caz3iMKH8PYR4HXXymr8fQWC1aKrkQ6wZDZD"

    return token
    

client = Bot(get_access_token("PYTHONWORKSHOPS"))  




@app.route('/print_qsts',methods = ['POST', 'GET'])
def print_qsts():
    qsts = pytraining.print_questions()
    return str(qsts)

@app.route('/get_qsts',methods = ['GET'])
def get_qsts_json():
    questions = pytraining.get_questions_json()
    
    return json.dumps(questions)

   

@app.route('/remove_qst',methods = ['GET'])
def remove_qst():
    pytraining.remove_question(request.args.get('id'))
    return "ok",200  


#handle message
@app.route('/talk/<msg>',methods = ['POST', 'GET'])
def talk(msg="Hi", sender_id=0):
    chatbot = ChatBot(
        'Pyson',
        trainer='chatterbot.trainers.ListTrainer',
        read_only=True
    )
    #msg = "Hi"
    reply = ""
    resp = chatbot.get_response(msg)
    if(resp.confidence > 0.5 and msg.upper() != "BYE"):
        reply = resp.serialize()
        reply = reply["text"]
    elif(msg.upper() != "BYE" and msg.upper() != "TEST BOT" ):
        reply = "NA"
        send_sample_questions(sender_id)
        if reply not in msg:
            pytraining.write_questions_to_db(msg)
    else:
        reply = "Thanks for talking to me, see you soon."
    return reply



#return response to messenger
def send_response(psid, response):
    #code to call graph api with response and token
    print(psid,response)
    client.send_text_message(psid,response)

def testbot(psid):
    client.send_message(psid,"I am testing the bot")
    #client.send_attachment_url(psid,"download: ","http://greenteapress.com/thinkpython/thinkpython.pdf")
    client.send_image_url(psid,"http://pythonworkshops.com/img/Raja.png")

def send_sample_questions(psid):
    buttons = []
    buttons.append(postback_button("Job Assurance?","Sample questions"))
    buttons.append(postback_button("Next workshop?","Sample questions"))
    buttons.append(postback_button("Schedule 3days workshop?","Sample questions"))
    buttons.append(postback_button("Workshop cost?","Sample questions"))
    client.send_button_message(psid,"Sorry Didn't get you? Try these questions,  ",buttons)
    
def link_button(button_title="Register",button_url="http://pythonworkshops.com/register"):    
    button = Button(title=button_title, type='web_url', url=button_url)
    return button

def postback_button(button_title="How can i register?",button_payload="Sample questions"):    
    button = Button(title=button_title, type='postback', payload=button_payload)
    return button
    
    '''button = Button(title='More questions', type='postback', payload='questions')
    buttons.append(button)
    client.send_button_message(psid,"Try: ",buttons)'''




#Verify Token 
@app.route('/token',methods = ['POST', 'GET'])
def verify_token(verify_tkn):
    token = get_access_token()
    if(verify_token==token):
        return True
    else:
        return False


#handle postback
def handle_postback(psid,recieved_postback):
    
    return ""
    
    
# Create a new chat bot named Pyson
@app.route('/support',methods = ['POST', 'GET'])
def support():
    global client
    if request.method == 'GET':
        mode = request.args.get('hub.mode')    
        verify_tkn = request.args.get('hub.verify_token')    
        challenge = request.args.get('hub.challenge') 
        if mode=="subscribe" and verify_token(verify_tkn):
            return challenge
    if request.method == 'POST':
        #handle_post_events(request) - if required
        input_request_data = json.loads(request.data.decode('utf8'))
        print("Input message - ",input_request_data)
        if input_request_data["object"] == "page":
            message_entries = input_request_data['entry']
            for entry in message_entries:
                if "messaging" in entry:
                    for event in entry["messaging"]:
                        if "message" in event:
                            message = event["message"]
                            sender_id = event["sender"]["id"]
                            recipient_id = event["recipient"]["id"]
                            if recipient_id == "483637655052155":
                                client = Bot(get_access_token("ESCHOOL"))  

                            if "text" in message:
                                if(message["text"].upper() == "TEST BOT"):
                                    testbot(sender_id)
                                else:
                                    resp = talk(message["text"],sender_id)
                                    print("Output Response - ",resp)
                                    send_response(sender_id, resp)
                            else:
                                print("None text message or event -", message)
                    
                    
    return "ok",200    

'''
Facebook Message formats
Text:
{'object': 'page', 'entry': [{'id': '2002681600054130', 'time': 1518265153750, 'messaging': [{'sender': {'id': '1752240531482295'}, 'recipient': {'id': '2002681600054130'}, 'timestamp': 1518265153172, 'message': {'mid': 'mid.$cAAcdbYf4xGtnsOz-lFhf6e0eExAp', 'seq': 63833, 'text': 'I dont know'}}]}]}

Postback:
{'object': 'page', 'entry': [{'id': '2002681600054130', 'time': 1518265683774, 'standby': [{'recipient': {'id': '2002681600054130'}, 'timestamp': 1518265683774, 'sender': {'id': '1752240531482295'}, 'postback': {'title': 'What is taught in 3 ...'}}]}]}



'''
#get all questions
@app.route('/get_all_qsts_ans',methods = ['GET'])
def get_all_qsts_ans():
    qsts_ans = pytraining.get_all_questions_answers_json()
    #print(type(qsts_ans))
    data={}
    for row in qsts_ans:
        #print(row[0],row[1],row[3],row[4])
        dict_id = row[0]
        data[dict_id] = {}
        data[dict_id]['qstn']= row[1]
        data[dict_id]['occurence']= row[3] 
        data[dict_id]['ans']= row[4]
    #print(type(data))
    #print(data)
    return json.dumps(data)

#Method to delete a particular record
@app.route('/delete_record',methods = ['GET'])
def delete_record():
    record_id = request.args.get('btn_id')
    record_id = int(record_id)
    result = pytraining.delete_single_record(record_id)
    return "ok",200

# secure method to train the bot, this should not be exposed to external people
@app.route('/train',methods = ['GET'])
def train():
    if request.method == 'GET':
        question = request.args.get('question')    
        answer = request.args.get('answer')
        trainbot = ChatBot(
        'Pyson',
        trainer='chatterbot.trainers.ListTrainer')
        trainbot.train([question,answer])
    return "ok",200          

@app.route('/register',methods= ['POST'])
def register_page_details():
    #print("Register page")
    page_id = request.form['page_id']
    access_token = request.form['access_token']
    database_name = request.form['database_name']
    page_url = request.form['page_url']
    contact_number = request.form['contact_number']
    contact_email = request.form['contact_email']
    contact_name = request.form['contact_name']
    pytraining.write_page_details_to_db(page_id,access_token,database_name,page_url,contact_number,contact_email,contact_name)
    return "ok",200


if __name__ == '__main__':
   app.run()




