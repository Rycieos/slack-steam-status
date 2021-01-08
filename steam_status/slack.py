from aiohttp.client_exceptions import ClientError
import asyncio
from fastapi.responses import JSONResponse
import hashlib
import hmac
import logging
import time

logger = logging.getLogger(__name__)
slack_request_header = {'Content-Type': 'application/x-www-form-urlencoded'}
encoding = 'utf-8'


class EphemeralTextResponse(JSONResponse):
  def __init__(self, content: str, **kwargs):
    super().__init__({
      "response_type": "ephemeral",
      "text": content
    }, **kwargs)

# Get permenant Slack OAuth token from temporary code
async def get_oauth_token(session, app_id, app_secret, code, redirect_uri):
  payload = 'client_id={}&client_secret={}&code={}&redirect_uri={}'.format(
      app_id, app_secret, code, redirect_uri)

  try:
    r = await session.post('https://slack.com/api/oauth.v2.access', data=payload,
        headers=slack_request_header)

    data = await r.json()
    return data['authed_user']['access_token']
  except (KeyError, ValueError, ClientError):
    logger.warn("Slack did not return a Oauth2 token", exc_info=True)
    return None

# Update a Slack user status
async def update_status(session, token, status="", emoji=""):
  # Construct the string to send to Slack
  payload = 'profile={{"status_text":"{}","status_emoji":"{}"}}&token={}'.format(
      status, emoji, token)

  try:
    r = await session.post('https://slack.com/api/users.profile.set',
        data=payload.encode('utf-8'), headers=slack_request_header)

    data = await r.json()
    return data['ok']
  except (KeyError, ValueError, ClientError):
    logger.warn("Failed to update Slack user status", exc_info=True)
    return False

def validate_request(body, timestamp, signature, secret):
  if abs(time.time() - timestamp) > 60 * 5:
    # The request timestamp is more than five minutes from local time.
    # It could be a replay attack, so let's ignore it.
    return False

  basestr = "v0:{}:{}".format(timestamp, body.decode(encoding))

  digest = hmac.new(secret.encode(encoding), basestr.encode(encoding), hashlib.sha256).hexdigest()
  return hmac.compare_digest(signature, "v0={}".format(digest))
