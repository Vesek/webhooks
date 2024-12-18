# Github Autodeploy
Written in Python using FastAPI.
Written mainly to make deploying manually a yesterday's chore, but also to learn FastAPI.

# Installation and configuration
`config.json` contains the actions you want to execute when a certain event happens in a repo
an example is available in the `config.json.example` file

To start you can use the `start.sh` script. It creates a python environment and install the dependencies in it, then starts the server.

If you want to run this in the background you can use the `webhook-github-autodeploy.service` file and run it using systemd.
Before installing this service file you need to first edit it so the `WorkingDirectory` path points here.

Running as non-root is highly recommended.

# TODO:
- [X] Check if config.json is in a valid format and if working dir and script actually exist
- [ ] Implement a QUEUE so repeated reqests don't collide
