#!/usr/bin/env python

import aiohttp
import asyncio
import logging
import time

import steam_status.db as db
import steam_status.slack as slack
import steam_status.steam as steam

logger = logging.getLogger(__name__)


class StatusDaemon:

  def __init__(self, http_session, steam_api_token):
      self.http_session = http_session
      self.steam_api_token = steam_api_token
      self.user_statuses = dict()

  async def check_status(self, user_ids):
    players = await steam.lookup_players(self.http_session, self.steam_api_token, user_ids.keys())

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
        if status == self.user_statuses[user]:
          continue
      except KeyError:
        # They have no remembered status
        logger.debug("First time seeing user '%s'", user)

        if not status:
          # And they are not in a game, so don't overwrite their Slack status
          self.user_statuses[user] = None
          continue

      logger.debug("%s: status to '%s'", user, status)

      if status:
        updated = await slack.update_status(self.http_session, user_ids[user], status, ":video_game:")
      else:
        updated = await slack.update_status(self.http_session, user_ids[user])

      if updated:
        # Only save their current status if the status update worked on Slack
        self.user_statuses[user] = status

  async def run(self):
    logger.info("Starting up Slack status update daemon")

    while True:
      users = await db.get_users()
      await self.check_status(users)
      await asyncio.sleep(30)

async def main(steam_api_token):
  async with aiohttp.ClientSession() as http_session:
    daemon = StatusDaemon(http_session, steam_api_token)
    await daemon.run()

if __name__ == "__main__":
  with open("steam_status_settings.py") as config:
    exec(config.read(), globals())

  loop = asyncio.get_event_loop()

  try:
    loop.run_until_complete(main(STEAM_API_TOKEN))
  except KeyboardInterrupt:
    pass
