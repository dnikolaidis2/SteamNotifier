from steam_notifier.app import run
from os import environ

if 'DISCORD_TOKEN' in environ:
    run(environ['DISCORD_TOKEN'])
else:
    raise Exception('No discord bot token provided.'
                    'Please define DISCORD_TOKEN environment variable.')
