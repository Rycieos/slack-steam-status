#!/usr/bin/env python

from steam_status.lib import get_users, slack_update_status, steam_lookup_players
import time

def check_status(user_ids, user_statuses):
  players = steam_lookup_players(STEAM_API_TOKEN, user_ids.keys())

  # Check that we got a response
  if not players:
    return

  # Get each players status, and push it to Slack if it has changed
  for player in players:
    user = player['steamid']
    try:
      status = player['gameextrainfo']
    except KeyError:
      # They are not in a game right now
      status = ""

    # Skip if no status change
    try:
      if status == user_statuses[user]:
        continue
    except KeyError:
      # They have no remembered status, but we will set it now
      pass

    user_statuses[user] = status

    if DEBUG:
      print("{}: status to '{}'".format(user, status))

    if status:
      slack_update_status(user_ids[user], status, ":video_game:")
    else:
      slack_update_status(user_ids[user])

if __name__ == "__main__":
  with open("steam_status_settings.py") as config:
    exec(config.read(), globals(), globals())

  users = get_users()

  # Set their status to blank. If they are in game, it will then be set, but if
  # they are not, we won't overwrite whatever they currently have
  user_statuses = dict.fromkeys(users.keys(),"")

  while True:
    check_status(users, user_statuses)
    time.sleep(50)
    users = get_users()
