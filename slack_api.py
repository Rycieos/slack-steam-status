#!/usr/bin/env python

from steam_status.lib import *
from flask import abort, Flask, redirect, request
import json

app = Flask(__name__)
slack_scope = "identify,users.profile:write"

with open("steam_status_settings.py") as config:
  exec(config.read(), globals(), globals())

# Endpoint for Slack app slash command. Returns a message with link to auth
@app.route('/steam_auth', methods=['POST'])
def add_user():
  if request.form.get('token', None) != SLACK_VERIFICATION_TOKEN:
    abort(401)

  text = request.form.get('text', None)
  if not text:
    return "Error: must pass in your steamID64 or vanity URL"

  steam_id = steam_resolve_vanityurl(STEAM_API_TOKEN, text)

  if not steam_id:
    steam_id = text

  if not steam_lookup_players(STEAM_API_TOKEN, [steam_id]):
    return "Error: not a valid steamID64 or vanity URL"

  return ("<https://slack.rycieos.com/api/slack_auth/{}|Click here> "
      "to enable status sync".format(steam_id))

# Endpoint for start of oauth dance
@app.route('/slack_auth/<steam_id>', methods=['GET'])
def auth(steam_id):
  return redirect("https://slack.com/oauth/authorize?"
      "client_id={}&scope={}&state={}".format(
      SLACK_APP_ID, slack_scope, steam_id), code=302)

# Endpoint for end of oauth dance. Save the user's oauth token
@app.route('/slack_after_auth', methods=['GET'])
def after_auth():
  code = request.args.get('code')
  steam_id = request.args.get('state')

  token = slack_get_oauth_token(SLACK_APP_ID, SLACK_APP_SECRET, code)

  if not token:
    return "Error: failed oauth dance!"

  # Add new user to user list
  user_ids = get_users()
  user_ids[steam_id] = token
  save_users(user_ids)

  return "Sync setup sucessful!"
