import aiohttp
import asyncio
import hashlib
import hmac
import time

slack_request_header = {'Content-Type': 'application/x-www-form-urlencoded'}
encoding = 'utf-8'

async def post(url, **kwargs):
  async with aiohttp.ClientSession() as session:
    return await session.post(url, **kwargs)

# Get permenant Slack OAuth token from temporary code
async def get_oauth_token(app_id, app_secret, code, redirect_uri):
  payload = 'client_id={}&client_secret={}&code={}&redirect_uri={}'.format(
      app_id, app_secret, code, redirect_uri)

  # POST to Slack
  r = await post('https://slack.com/api/oauth.v2.access', data=payload,
      headers=slack_request_header)

  try:
    data = await r.json()
    return data['authed_user']['access_token']
  except (KeyError, ValueError):
    return None

# Update a Slack user status
async def update_status(token, status="", emoji=""):
  # Construct the string to send to Slack
  payload = 'profile={{"status_text":"{}","status_emoji":"{}"}}&token={}'.format(
      status, emoji, token)

  # POST to Slack
  await post('https://slack.com/api/users.profile.set',
      data=payload.encode('utf-8'), headers=slack_request_header)

def validate_request(body, timestamp, signature, secret):
  if abs(time.time() - timestamp) > 60 * 5:
    # The request timestamp is more than five minutes from local time.
    # It could be a replay attack, so let's ignore it.
    return False

  basestr = "v0:{}:{}".format(timestamp, body.decode(encoding))

  digest = hmac.new(secret.encode(encoding), basestr.encode(encoding), hashlib.sha256).hexdigest()
  return hmac.compare_digest(signature, "v0={}".format(digest))
