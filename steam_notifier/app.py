from steam_notifier.models.model import db, Mod
from steam_notifier.steam.api import PublishedFileDetails
from discord import Client
from re import compile
import asyncio
import signal

# arma 3 app id 107410

db.connect()
db.create_tables([Mod])

channels = {}


async def send_message(channel, messages):
    message = ""
    message_length = 0
    for message_part in messages:
        if message_length + len(message_part) + 1 >= 2000:
            await channel.send(message)
            message = ""
            message_length = 0

        message += message_part + "\n"
        message_length += len(message_part) + 1

    if message != "":
        message = message.rstrip('\n')
        await channel.send(message)


class NotifierBot(Client):
    track_prog = compile(r"(^~track )(([0-9]*)((,|$)))*")
    untrack_prog = compile(r"(^~untrack )(([0-9]*)((,|$)))*")

    async def on_ready(self):
        global channels
        try:
            channel_ids = [mod.discord_channel_id for mod in Mod.select()]
        except Exception:
            pass
        else:
            channel_ids = list(set(channel_ids))
            for channel in channel_ids:
                channels[channel] = self.get_channel(channel)

        print('Logged on as {0}!'.format(self.user))

    async def on_message(self, message):
        if message.author == client.user:
            return

        if message.content.startswith('~'):
            if self.track_prog.fullmatch(message.content):
                mod_ids = message.content.lstrip("~track ").split(',')
                for i in range(len(mod_ids)):
                    mod_ids[i] = int(mod_ids[i])

                mods = PublishedFileDetails.get_details(mod_ids)
                messages = []
                for mod in mods:
                    if mod.result == 1:
                        if mod.consumer_app_id != 107410:  # Arma 3 id
                            messages.append(f"Mod {mod.publishedfileid} is not an Arma 3 mod")
                        else:
                            mod_db, created = Mod.get_or_create(steam_id=mod.publishedfileid,
                                                                name=mod.title,
                                                                last_updated=mod.time_updated,
                                                                discord_channel_id=message.channel.id)
                            if created:
                                messages.append(f"Mod '{mod_db.name}' with id {mod_db.steam_id}"
                                                f" added to the tracking list")
                                global channels
                                if mod_db.discord_channel_id not in channels:
                                    channels[mod_db.discord_channel_id] = self.get_channel(mod_db.discord_channel_id)
                            else:
                                messages.append(f"Mod {mod.publishedfileid} is already in the tracking list")
                    else:
                        messages.append(f"Invalid mod id {mod.publishedfileid}")

                await send_message(message.channel, messages)

            elif self.untrack_prog.fullmatch(message.content):
                mod_ids = message.content.lstrip("~untrack ").split(',')
                for i in range(len(mod_ids)):
                    mod_ids[i] = int(mod_ids[i])

                messages = []
                for mod_id in mod_ids:
                    db_mod = Mod.delete().where(Mod.steam_id == mod_id, Mod.discord_channel_id == message.channel.id)
                    if db_mod.execute() != 1:
                        messages.append("Unexpected behavior occurred!")
                    else:
                        messages.append(f"Removed mod with id {mod_id} from tracking list")

                await send_message(message.channel, messages)

            elif message.content == "~list":
                try:
                    mods = [mod for mod in Mod.select().where(Mod.discord_channel_id == message.channel.id)]
                except Exception:
                    pass
                else:
                    if len(mods) == 0:
                        await message.channel.send("No mods being tracked at the moment")
                    else:
                        messages = []
                        for mod in mods:
                            messages.append(f"{mod.name} ({mod.steam_id})")

                        await send_message(message.channel, messages)

            elif message.content == "~help":
                await message.channel.send(f"Usage: ~list | ~untrack | ~track\n\n"
                                           f"~list\tlists all tracked mods.\n"
                                           f"~track ID1[,ID2,ID3...]\ttrack 1 or more mods by their id's.\n"
                                           f"~untrack ID1[,ID2,ID3...]\tuntrack 1 or mod mods by their id's")


client = NotifierBot()


async def mod_update_tracker(wait):
    await asyncio.sleep(60)
    global channels
    while True:
        try:
            mods_db = [mod for mod in Mod.select()]
            mod_ids = [mod.steam_id for mod in mods_db]
        except Exception:
            pass
        else:
            if len(mods_db) != 0:
                mods = PublishedFileDetails.get_details(mod_ids)
                for mod in mods:
                    for db_mod in mods_db:
                        if mod.publishedfileid == db_mod.steam_id:
                            if mod.time_updated > db_mod.last_updated:
                                await channels[db_mod.discord_channel_id].send(f"Mod '{db_mod.name}' has been updated!\n"
                                                                               f"https://steamcommunity.com/workshop"
                                                                               f"/filedetails/?id={db_mod.steam_id}")
                                db_mod.last_updated = mod.time_updated
                                db_mod.save()

        await asyncio.sleep(wait)


def run(discord_token, wait):
    loop = asyncio.get_event_loop()

    try:
        loop.add_signal_handler(signal.SIGINT, lambda: loop.stop())
        loop.add_signal_handler(signal.SIGTERM, lambda: loop.stop())
    except NotImplementedError:
        pass

    loop.create_task(mod_update_tracker(wait))
    loop.create_task(client.start(discord_token))
    loop.run_forever()

