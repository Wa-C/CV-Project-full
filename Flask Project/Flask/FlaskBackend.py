from flask import Flask, request, render_template,session, redirect, url_for
from flask_sock import Sock
import config
from flask_socketio import SocketIO
from flask_socketio import emit
import os
import sys
import json

app = Flask(__name__)
app.secret_key = config.SECRET_KEY  # Set a secret key for session encryption



@app.route('/')
def index():
    name = 'John Doe'
    age = 30
    return render_template('index.html', name=name, age=age)
    


@app.route('/update_coin_sum', methods=['POST'])
def update_coin_sum():
    data = request.json.get('coinSum')
    session['coin_sum'] = data
    return redirect(url_for('coinCount'))
    
@app.route('/coinCount', methods=['GET'])
def coinCount():
    coin_sum = session.get('coin_sum')
    print(coin_sum)
    return render_template('coinCount.html', coin_sum=coin_sum)
    
    

if __name__ == '__main__':
    app.run()

