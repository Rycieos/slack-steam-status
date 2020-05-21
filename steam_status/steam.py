import aiohttp
import asyncio

async def get(url, **kwargs):
  async with aiohttp.ClientSession() as session:
    return await session.get(url, **kwargs)

# Return player summaries for the list of SteamIDs
async def lookup_players(token, steam_ids):
  # TODO limit to 100 users at a time
  ids_string = ','.join(steam_ids)

  # Get the user statuses from Steam
  r = await get("https://api.steampowered.com/ISteamUser/GetPlayerSummaries/"
      "v0002/?key={}&steamids={}".format(token, ids_string))

  try:
    data = await r.json()
    return data['response']['players']
  except (KeyError, ValueError):
    return None

# Returns the SteamID for the vanity url. Does not have to be a valid url
async def resolve_vanityurl(token, vanity_url):
  r = await get("https://api.steampowered.com/ISteamUser/ResolveVanityURL/"
      "v0001/?key={}&vanityurl={}".format(token, vanity_url))

  # Return a value if Steam found one
  try:
    data = await r.json()
    return data['response']['steamid']
  except (KeyError, ValueError):
    return None
