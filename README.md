# slack-steam-status

[![Docker Image Version](https://img.shields.io/docker/v/rycieos/slack-steam-status?sort=semver)
 ![Docker Pulls](https://img.shields.io/docker/pulls/rycieos/slack-steam-status)](https://hub.docker.com/repository/docker/rycieos/slack-steam-status)
[![Docker Build Status](https://img.shields.io/docker/cloud/build/rycieos/slack-steam-status)](https://hub.docker.com/repository/docker/rycieos/slack-steam-status/builds)
[![Docker Image Size](https://img.shields.io/docker/image-size/rycieos/slack-steam-status?sort=semver)](https://hub.docker.com/repository/docker/rycieos/slack-steam-status/tags)

Slack app to sync Steam game status to Slack status

## Setup
You will need to create a new Slack app to gain the OAuth permissions from
your users to modify their Slack statuses.

### Create app
On the [Create a Slack App](https://api.slack.com/apps?new_app=1) screen,
fill out the form with "Steam Status" as the app name.

The app does not have a "bot" user, so you will probably want to turn those
features off.

You will need to register a new "Slash Command":

| Option            | Value
| ----------------- | -----
| Command           | `/steam-status`
| Request URL       | `<your-base-url>/api/steam_auth`
| Short Description | Register your Steam user to sync statuses
| Usage Hint        | `<steamID64 or vanityURL>`

Under Oauth scopes, you need the `commands` bot token scope, and the
`users.profile:write` user token scope.

Then install the Slack app for your workspace.

### Steam API
You will need a [Steam Web API key](https://steamcommunity.com/dev/apikey) to
access the Steam Player API.

### Configuration
The app API needs the app keys and tokens from Slack and Steam to function.
Copy the `steam_status_settings.py.dist` file to `steam_status_settings.py`,
and replace the fake strings with your own:

| Variable             | Value
| -------------------- | -----
| HTTP_BASE_URL        | The protocol and base URL of the server. This can not be detected by the app if the app is behind a reverse proxy or redirected from Slack, so this needs to be set.
| STEAM_API_TOKEN      | The Steam Web API token used to read player statuses.
| SLACK_APP_ID         | The Slack app client ID, like `000000000000.000000000000`. Note this is different from the Slack app ID, which is shorter.
| SLACK_APP_SECRET     | The Slack app secret, from the App general page (`https://api.slack.com/apps/<app-id>/general`).
| SLACK_SIGNING_SECRET | The Slack signing secret, from the App general page (`https://api.slack.com/apps/<app-id>/general`). Note this is different than the Verification Token, which is less secure.

## Running
The app can be run with any ASGI server, like uvicorn, or the in the provided
Docker image. The app API server and the status daemon will run in the same
process.

### uvicorn
Running with `uvicorn` is simple:
```
uvicorn slack_api:app
```

### Docker
There is a Docker image build off of `tiangolo/uvicorn-gunicorn`, so any
environment vars can be used from
[that image](https://github.com/tiangolo/uvicorn-gunicorn-docker#environment-variables).

#### Docker usage
To run `slack-steam-status` in its own container, you only need to make a few
changes.
 * The `steam_status_settings.py` config file must be mounted in the container.
 * The port that the web API server will listen on needs to be specified.
   Like any other HTTP server, it can sit behind a reverse proxy (and probably
   should, so you can enable HTTPS).

All together, the run command would look like this:
```
docker run \
  -v ./steam_status_settings.py:/app/steam_status_settings.py:ro \
  -p 80:80 \
  rycieos/slack-steam-status
```

#### Docker compose
If you want to use docker-compose:
```yml
version: '3'
services:
  slack-steam-status:
    image: rycieos/slack-steam-status
    restart: always
    ports:
      - 80:80
    volumes:
      - ./steam_status_settings.py:/app/steam_status_settings.py:ro
```
