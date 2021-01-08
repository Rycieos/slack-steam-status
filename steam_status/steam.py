from aiohttp.client_exceptions import ClientError
import asyncio
import logging

logger = logging.getLogger(__name__)


# Return player summaries for the list of SteamIDs
async def lookup_players(session, token, steam_ids):
  # TODO limit to 100 users at a time
  ids_string = ','.join(steam_ids)

  try:
    # Get the user statuses from Steam
    r = await session.get("https://api.steampowered.com/ISteamUser/GetPlayerSummaries/"
        "v0002/?key={}&steamids={}".format(token, ids_string))

    data = await r.json()
    return data['response']['players']
  except (KeyError, ValueError, ClientError):
    logger.warn("Steam returned no players", exc_info=True)
    return None

# Returns the SteamID for the vanity url. Does not have to be a valid url
async def resolve_vanityurl(session, token, vanity_url):
  try:
    r = await session.get("https://api.steampowered.com/ISteamUser/ResolveVanityURL/"
        "v0001/?key={}&vanityurl={}".format(token, vanity_url))

    data = await r.json()
    return data['response']['steamid']
  except (KeyError, ValueError, ClientError):
    logger.debug("Steam returned no SteamID for vanity slug '%s'", vanity_url,
        exc_info=True)
    return None
