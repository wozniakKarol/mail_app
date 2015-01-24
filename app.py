#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask_bootstrap import Bootstrap
from datetime import datetime
from flask import Flask, jsonify, render_template, request, session, redirect, url_for
from urllib2 import Request, urlopen, HTTPError
import json, os

app = Flask(__name__)
Bootstrap(app)
app.secret_key = os.urandom(32)
lastTime = ""
mailprefix='http://len.iem.pw.edu.pl/staff/~chaberb/apps/mail'
prefix = '/~wozniak2/apps/mail_app'
from werkzeug.debug import DebuggedApplication
app.wsgi_app = DebuggedApplication(app.wsgi_app, evalex=True)
app.debug = True

@app.route(prefix +'/')
def home():
    return render_template('home.html')

@app.route(prefix + '/welcome')
def welcome():
    return render_template('welcome.html')


@app.route(prefix + '/log', methods=['GET', 'POST'])
def log():
    if request.method == 'POST':
        try:
            myrequest = Request(mailprefix + '/user')
            allusers = json.loads(urlopen(myrequest).read())
            user_password = request.form['password']
            headers = {"Content-Type": "text/plain"}
            myrequest = Reques(mailprefix + '/login/' + request.form['username'], data = user_password, headers = headers)
            response_body = json.loads(urlopen(myrequest).read())
            if response_body['msg'] == 'credentials correct':
                session['logged_in']=True
                session['username'] = request.form['username']
                for user in allusers:
                    if session['username'] == user['username']:
                        session['user_id'] = user['user_id']
                        return redirect(url_for('hello'))
                    else:
                        return render_template('log.html',error='Invalid username or password. Try again!')
        except HTTPError:
            error = 'Invalid username or password. Try again!'
            pass
            return render_template('log.html', error=error)
    if request.method == 'GET':
        if 'username' in session:
            global lastTime
            if session['logged_in'] == True :
                try:
                    lastTime = session['lastTime']
                except KeyError:
                    lastTime = ''
                session['lastTime'] = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                session['logged_in'] = False
                url = mailprefix+ '/user/' + str(session['user_id']) + '/unread_count'
                myrequest = Reques(url)
                unreadcount = json.loads(urlopen(myrequest ).read())
            return render_template('hello.html', username = session['username'], time=lastTime, unread_count = unreadcount['unread']) 
    return render_template('log.html')

@app.route(prefix + '/hello')
def hello():
    if 'username' in session:
        global lastTime
        if session['logged_in'] == True :
            try:
                lastTime = session['lastTime']
            except KeyError:
                lastTime = ''
            session['lastTime'] = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            session['logged_in'] = False
            url = mailprefix+ '/user/' + str(session['user_id']) + '/unread_count'
            myrequest = Reques(url)
            unreadcount = json.loads(urlopen(myrequest ).read())
        return render_template('hello.html', username = session['username'], time=lastTime, unread_count = unreadcount['unread'])
    return render_template('log.html')

@app.route(prefix + '/get_user_name')
def get_user_name():
        myrequest  = Request( mailprefix+'/user/' + request.args.get('a', 0, type=str) )
        user = json.loads(urlopen(myrequest).read())
        return jsonify(user=user)

@app.route(prefix + '/inbox')
def inbox():
        inbox=[]
        myrequest  = Request(mailprefix+'/user/' + str(session['user_id']) + '/messages' )
        messages= json.loads(urlopen(myrequest).read())
        for message in messages:
                if message['type'] == 'inbox':
                        inbox.append(message)
        return jsonify(inbox=inbox)

@app.route(prefix + '/send', methods=['POST'])
def send():
        session['logged_in']=True
        myrequest  = Request(mailprefix+'/user')
        users = json.loads(urlopen(myrequest).read())
        for user in users:
                if user['username'] == request.form['to_user']:
                        message_content = request.form['content']
                        message_title= request.form['title']
                        user_id = user['user_id']
                        values = json.dumps({"content": message_content, "to_user_id": user_id, "title": message_title, "from_user_id": session['user_id']})
                        headers = {"Content-Type": "application/json"}
                        myrequest  = Request(mailprefix+'/msg', data = values, headers = headers)
                        response_body = urlopen(myrequest).read()
                        url = mailprefix+ '/user/' + str(session['user_id']) + '/unread_count'
                        myrequest  = Request(url)
                        unreadcount = json.loads(urlopen(myrequest).read())
                        unread= unreadcount['unread']
                        return render_template('hello.html', message="Send!", unread_count= unread, username=session['username'], time='')
        url = mailprefix+ '/user/' + str(session['user_id']) + '/unread_count'
        myrequest  = Request(url)
        unreadcount = json.loads(urlopen(myrequest ).read())
        unread= unreadcount['unread']
        return render_template('hello.html', promt="Unsend!", unread_count= unread, username = session['username'], time='')


@app.route(prefix + '/sentmessages')
def sentmessages():
        myrequest = Request(mailprefix+'/user/'+ str(session['user_id']) + '/messages')
        messages = json.loads(urlopen(myrequest).read())
        sentmessages = []
        for message in messages:
                if message['type'] == 'outbox':
                        sentmessages.append(message)
        return jsonify(message=sentmessages)

@app.route(prefix + '/delete')
def delete():
        try:
                message = request.args.get('a', 0, type=str)
                myrequest  = Request(mailprefix+ '/msg/' + message)
                myrequest.get_method = lambda: 'DELETE'
                response_body = urlopen(myrequest).read()
                myrequest  = Request(mailprefix+ '/user/' + str(session['user_id']) + '/unread_count')
                unreadcount= json.loads(urlopen (myrequest).read())
                unread= unreadcount['unread']
                return jsonify(message="Message delete!", unread_count= unread)
        except HTTPError:
                myrequest = Request(mailprefix + '/user/' + str(session['user_id']) +'/unread_count')
                unreadcount = json.loads(urlopen(myrequest ).read())
                unread= unreadcount['unread']
                return jsonify(message="Message delete!", unread_count= unread)

@app.route(prefix + '/read_message')
def read_message():
        idmessage= request.args.get('a', 0, type=str)
        myrequest = Request(mailprefix+'/msg/' + idmessage+ '/read')
        urlopen(myrequest)
        myrequest  = Request(mailprefix+ '/msg/' + idmessage)
        message = json.loads(urlopen(myrequest).read())
        myrequest = Request(mailprefix + '/user/' + str(session['user_id']) +'/unread_count')
        unreadcount = json.loads(urlopen(myrequest ).read())
        unread= unreadcount['unread']
        return jsonify(message=message, unread_count= unread)


@app.route(prefix + '/logout')
def logout():
        message = 'You were logged out.'
        session.pop('username', None)
        return render_template('log.html', message=message)


if __name__ == '__main__':
        app.run()
