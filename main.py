from steam_notifier.app import run
from os import environ

if 'DISCORD_TOKEN' in environ:
	sleep_time = 10*60

	if 'SLEEP_TIME' in environ:
		sleep_time = int(environ['SLEEP_TIME'])

	run(environ['DISCORD_TOKEN'], sleep_time)
else:
	raise Exception('No discord bot token provided.'
		'Please define DISCORD_TOKEN environment variable.')
