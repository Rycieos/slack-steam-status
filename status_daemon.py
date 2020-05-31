#!/usr/bin/env python

import asyncio
import logging
import time

import steam_status.db as db
import steam_status.slack as slack
import steam_status.steam as steam

logger = logging.getLogger(__name__)


async def check_status(steam_api_token, user_ids, user_statuses):
  players = await steam.lookup_players(steam_api_token, user_ids.keys())

  # Check that we got a response
  if not players:
    logger.warn("Empty response from Steam API")
    return

  # Get each players status, and push it to Slack if it has changed
  for player in players:
    user = player['steamid']
    try:
      status = player['gameextrainfo']
    except KeyError:
      # They are not in a game right now
      status = None

    # Skip if no status change
    try:
      if status == user_statuses[user]:
        continue
    except KeyError:
      # They have no remembered status
      logger.debug("First time seeing user '%s'", user)

      if not status:
        # And they are not in a game, so don't overwrite their Slack status
        user_statuses[user] = None
        continue

    logger.debug("%s: status to '%s'", user, status)

    if status:
      updated = await slack.update_status(user_ids[user], status, ":video_game:")
    else:
      updated = await slack.update_status(user_ids[user])

    if updated:
      # Only save their current status if the status update worked on Slack
      user_statuses[user] = status

async def status_daemon(steam_api_token):
  logger.info("Starting up Slack status update daemon")

  user_statuses = dict()

  while True:
    users = await db.get_users()
    await check_status(steam_api_token, users, user_statuses)
    await asyncio.sleep(30)

def main():
  with open("steam_status_settings.py") as config:
    exec(config.read(), globals())

  loop = asyncio.get_event_loop()

  try:
    loop.run_until_complete(status_daemon(STEAM_API_TOKEN))
  except KeyboardInterrupt:
    pass

if __name__ == "__main__":
  main()
