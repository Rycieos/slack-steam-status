import aiohttp
import asyncio

slack_request_header = {'Content-Type': 'application/x-www-form-urlencoded'}

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
