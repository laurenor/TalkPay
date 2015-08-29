from flask import Flask, redirect, url_for, session, request, jsonify, render_template
from flask_oauthlib.client import OAuth
import os
from flask_debugtoolbar import DebugToolbarExtension
from model import connect_to_db, db
from jinja2 import StrictUndefined
from twilio import twiml
from twilio.rest import TwilioRestClient
from model import connect_to_db, db, User, Position



app = Flask(__name__)
app.debug = True
app.secret_key = 'development'
oauth = OAuth(app)

linkedin = oauth.remote_app(
    'linkedin',

    consumer_key=os.environ['CLIENT_ID'],  # replace with you own Client ID
    consumer_secret=os.environ['CLIENT_SECRET'], # replace with your consumer_secret


    request_token_params={
        'scope': 'r_basicprofile', # replace with r_fullprofile
        'state': 'RandomString',
    },
    base_url='https://api.linkedin.com/v1/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://www.linkedin.com/uas/oauth2/accessToken',
    authorize_url='https://www.linkedin.com/uas/oauth2/authorization',
)


@app.route('/')
def index():
    if 'linkedin_token' in session:
        return render_template('dashboard.html')
    return redirect(url_for('login'))


app.secret_key = "developHER"
app.jinja_env.undefined = StrictUndefined


##############################################################################
# **** Twilio **** 

account_sid = os.environ['TWILIO_ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']
client = TwilioRestClient(account_sid, auth_token)
to_number = os.environ['TWILIO_TO_NUMBER']
TWILIO_NUMBER = os.environ['TWILIO_NUMBER']

##############################################################################

@app.route('/login')
def login():
    return linkedin.authorize(callback=url_for('authorized', _external=True))

@app.route('/logout')
def logout():
    session.pop('linkedin_token', None)
    return render_template("index.html")

@app.route('/login/authorized')
def authorized():
    resp = linkedin.authorized_response()
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    session['linkedin_token'] = (resp['access_token'], '')
    me = linkedin.get('people/~:(id,first-name,last-name,headline,positions,location,industry,specialties,public-profile-url)?format=json')
    user_data = me.data
    first_name = user_data.get('firstName', None)
    last_name = user_data.get('lastName', None)
    headline = user_data.get('headline', None)
    industry = user_data.get('industry', None)
    location = user_data.get('location', None)
    if location:
        location_name = location['name']

    positions = user_data.get('positions', None)
    if positions and positions.get('values', None):
        position_info = positions.get('values')[0]
        if position_info.get('company', None):
            position_company = position_info.get('company', None)['name']
        if position_info.get('startDate', None):
            position_start_date_month = position_info['startDate']['month']
            position_start_date_year = position_info['startDate']['year']
        if position_info.get('title', None):
            position_title = position_info['title']



    user = User.create(first_name=first_name,
                last_name=last_name,
                headline=headline,
                industry=industry,
                location=location
                )
    user_id = user.user_id


    return render_template('dashboard.html')


@linkedin.tokengetter
def get_linkedin_oauth_token():
    return session.get('linkedin_token')


def change_linkedin_query(uri, headers, body):
    auth = headers.pop('Authorization')
    headers['x-li-format'] = 'json'
    if auth:
        auth = auth.replace('Bearer', '').strip()
        if '?' in uri:
            uri += '&oauth2_access_token=' + auth
        else:
            uri += '?oauth2_access_token=' + auth
    return uri, headers, body

linkedin.pre_request = change_linkedin_query


if __name__ == '__main__':
    app.debug = True

    connect_to_db(app)


    # DebugToolbarExtension(app)
    app.run()