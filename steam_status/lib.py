import json
import requests

slack_request_header = {'Content-Type': 'application/x-www-form-urlencoded'}
users_filename = "users.json"

# Get saved list of registered users, with Steam ID and Slack token
def get_users():
  try:
    with open(users_filename) as users_file:
      return json.load(users_file)
  except (IOError, ValueError):
    return {}

# Save users dictonary to file DB
def save_users(users):
  with open(users_filename, 'w') as users_file:
    json.dump(users, users_file)

# Get permenant Slack OAuth token from temporary code
def slack_get_oauth_token(app_id, app_secret, code, redirect_uri):
  payload = 'client_id={}&client_secret={}&code={}&redirect_uri={}'.format(
      app_id, app_secret, code, redirect_uri)

  # POST to Slack
  r = requests.post('https://slack.com/api/oauth.v2.access', data=payload,
      headers=slack_request_header)

  try:
    data = r.json()
    return data['authed_user']['access_token']
  except (KeyError, ValueError):
    return None

# Update a Slack user status
def slack_update_status(token, status="", emoji=""):
  # Construct the string to send to Slack
  payload = 'profile={{"status_text":"{}","status_emoji":"{}"}}&token={}'.format(
      status, emoji, token)

  # POST to Slack
  requests.post('https://slack.com/api/users.profile.set',
      data=payload.encode('utf-8'), headers=slack_request_header)

# Return player summaries for the list of SteamIDs
def steam_lookup_players(token, steam_ids):
  # TODO limit to 100 users at a time
  ids_string = ','.join(steam_ids)

  # Get the user statuses from Steam
  r = requests.get("https://api.steampowered.com/ISteamUser/GetPlayerSummaries/"
      "v0002/?key={}&steamids={}".format(token, ids_string))
  try:
    data = r.json()
    return data['response']['players']
  except (KeyError, ValueError):
    return None

# Returns the SteamID for the vanity url. Does not have to be a valid url
def steam_resolve_vanityurl(token, vanity_url):
  r = requests.get("https://api.steampowered.com/ISteamUser/ResolveVanityURL/"
      "v0001/?key={}&vanityurl={}".format(token, vanity_url))

  # Return a value if Steam found one
  try:
    data = r.json()
    return data['response']['steamid']
  except (KeyError, ValueError):
    return None
