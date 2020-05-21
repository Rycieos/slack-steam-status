import aiofiles
import asyncio
import json

users_filename = "users.json"

# Get saved list of registered users, with Steam ID and Slack token
async def get_users():
  try:
    async with aiofiles.open(users_filename) as users_file:
      contents = await users_file.read()
      return json.loads(contents)
  except (IOError, ValueError):
    return {}

# Save users dictonary to file DB
async def save_users(users):
  async with aiofiles.open(users_filename, 'w') as users_file:
    contents = json.dumps(users)
    await users_file.write(contents)
