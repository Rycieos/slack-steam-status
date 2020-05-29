#!/usr/bin/env python

import asyncio
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import RedirectResponse
import logging

import steam_status.db as db
import steam_status.slack as slack
import steam_status.steam as steam
from status_daemon import status_daemon

app = FastAPI()
logger = logging.getLogger(__name__)
SLACK_SCOPE = "users.profile:write"

with open("steam_status_settings.py") as config:
  exec(config.read())

@app.on_event("startup")
async def startup_daemon():
  asyncio.get_event_loop().create_task(status_daemon(STEAM_API_TOKEN))

# Endpoint for Slack app slash command. Returns a message with link to auth
@app.post('/api/steam_auth', response_class=slack.EphemeralTextResponse)
async def add_user(request: Request,
                   x_slack_request_timestamp: int = Header(...),
                   x_slack_signature: str = Header(...),
  ):

  if not slack.validate_request(await request.body(), x_slack_request_timestamp,
          x_slack_signature, SLACK_SIGNING_SECRET):
    raise HTTPException(status_code=403, detail="No valid Slack source token")

  form_data = await request.form()
  text = form_data['text']
  if not text:
    logger.debug("User called command without an argument")
    return "Error: must pass in your steamID64 or vanity URL"

  steam_id = await steam.resolve_vanityurl(STEAM_API_TOKEN, text)

  if not steam_id:
    logger.debug("Lookup of vanity URL for string '%s' failed", text)
    steam_id = text

  if not await steam.lookup_players(STEAM_API_TOKEN, [steam_id]):
    logger.debug("String '%s' not a valid Steam ID", steam_id)
    return "Error: not a valid steamID64 or vanity URL"

  return "<{}{}|Click here> to enable Steam status syncing".format(
          HTTP_BASE_URL, app.url_path_for("auth", steam_id=steam_id))

# Endpoint for start of oauth dance
@app.get('/api/slack_auth/{steam_id}')
def auth(steam_id: str):
  return RedirectResponse("https://slack.com/oauth/v2/authorize?"
      "client_id={}&user_scope={}&state={}&redirect_uri={}{}".format(
      SLACK_APP_ID, SLACK_SCOPE, steam_id, HTTP_BASE_URL, app.url_path_for("after_auth")))

# Endpoint for end of oauth dance. Save the user's oauth token
@app.get('/api/slack_after_auth', status_code=201)
async def after_auth(code: str, state: str):
  steam_id = state

  token = await slack.get_oauth_token(SLACK_APP_ID, SLACK_APP_SECRET,
      code, HTTP_BASE_URL + app.url_path_for("after_auth"))

  if not token:
    return "Error: failed oauth dance!"

  # Add new user to user list
  user_ids = await db.get_users()
  user_ids[steam_id] = token
  await db.save_users(user_ids)

  return "Sync setup sucessful!"
