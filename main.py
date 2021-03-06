# Imports
from math import ceil
from os import path
from datetime import datetime
import json
import socket
import discord
import discord.ext.commands
from mrbill import Bill

from create_thread import create_thread, create_thread_message

# Local imports
from log_handling import *

hostname = socket.gethostname()

VERSION = "1.0"
TOKEN = ""
PREFIX = "."
DEBUG = "true"
LEVEL = "debug"


def setup_config():
	global TOKEN, PREFIX, DEBUG, LEVEL, JOKE_SERVERS, DEFAULT_COLOUR

	def initiate_const(name, default, dictionary):
		try:
			return dictionary[name]
		except KeyError:
			return default

	if not path.exists("config.json"):
		configFile = open("config.json", "w")
		json.dump(
			{
				"token": TOKEN,
				"prefix": PREFIX,
				"debug": DEBUG,
				"level": LEVEL
			},
			configFile, indent=4
		)
	else:
		with open("config.json", encoding='utf-8') as file:
			data = json.load(file)
			TOKEN = initiate_const("token", TOKEN, data)
			PREFIX = initiate_const("prefix", PREFIX, data)
			DEBUG = initiate_const("debug", DEBUG, data)
			LEVEL = initiate_const("level", LEVEL, data)

setup_config()

# Definitions
class MyClient(discord.ext.commands.Bot):

	def __init__(self, *args, **kwargs):
		"""Constructor."""

		super().__init__(*args, **kwargs,command_prefix=PREFIX)
		self.connected = True  # Starts true so on first boot, it won't think its restarted
		self.start_time = datetime.now()
		self.last_disconnect = datetime.now()
		self.activity = discord.Activity(type=discord.ActivityType.streaming, name="with your money")

		# Prints logs to the console
		if DEBUG is True:
			x = logging.StreamHandler()
			x.setLevel(LEVEL)
			logger.addHandler(x)

	def get_uptime(self):
		"""Returns instance uptime."""

		try:
			seconds = round((datetime.now() - self.start_time).total_seconds())
			uptime = ""
			if seconds >= 3600:
				uptime += str(seconds // 3600) + " "
				if seconds // 3600 == 1:
					uptime += "hour"
				else:
					uptime += "hours"
			if seconds % 3600 >= 60:
				if uptime != "":
					uptime += " "
				uptime += str(seconds % 3600 // 60) + " "
				if seconds % 3600 // 60 == 1:
					uptime += "minute"
				else:
					uptime += "minutes"
			if seconds % 60 > 0:
				if uptime != "":
					uptime += " "
				uptime += str(seconds % 60) + " "
				if seconds % 60 == 1:
					uptime += "second"
				else:
					uptime += "seconds"
			logger.debug("Calculated uptime")  # Event log
			return uptime
		except Exception as exception:
			logger.error("Failed to calculate uptime. Exception: " + exception)  # Event log
			return None

	async def on_ready(self):
		"""Runs when the client is ready."""

		logger.debug("Connected!")

		if self.connected == False:
			logger.info("Last disconnect was " + str(self.last_disconnect))
		self.connected = True

		logger.info(self.user.name + " is ready (finished on_ready)")  # Event log

		# Log on_ready messages
		logger.info(self.user.name + " is ready (commencing on_ready)")  # Event log
		if self.guilds != []:
			logger.info(self.user.name + " is connected to the following guilds:")  # Event log
			for guild in self.guilds:
				logger.info("    " + guild.name + " (ID: " + str(guild.id) + ")")  # Event log

	async def on_disconnect(self):
		"""Runs on disconnection.
		Logs disconnection."""

		if self.connected == True:  # Stops code being ran every time discord realises its still disconnected since the last minute or so
			logger.info("Bot disconnected")
			self.last_disconnect = datetime.now()
			self.connected = False

	async def on_message(self, message):
		"""Runs on message."""

		logger.debug("Message sent by " + message.author.name)  # Event log

		# Don't respond to yourself
		if message.author.id == self.user.id:
			return

		# Don't respond to other bots
		if message.author.bot is True:
			return

		if len(message.attachments) > 0:
			if message.attachments[0].content_type.startswith("text/plain"):
				#print(message.attachments[0].url)
				biller = Bill.Bill(path=message.attachments[0].url)
				await message.channel.send("Attachments are not fully supported but we'll have a go...")
		else:
			if message.content.startswith("```"):
				message.content = message.content[3:-3]
			biller = Bill.Bill(text=message.content)
		totalsPrintout = biller.getTotalsPrintout()
		totalsPrintout = discord.Embed(title=f"Bill of ??{round(biller.totalCost)}",description=totalsPrintout,colour=0X378805)
		if len(biller.items) != 0:
			thread = await message.channel.create_thread(name=f"Bill of ??{round(biller.totalCost)}", minutes=60, message=message)

			await create_thread_message(TOKEN, thread, content=None,embeds=totalsPrintout) # Sends message in newly created thread

		if message.content.startswith(PREFIX):
			message.content = message.content[1:]
			# Locate command
			if message.content == "locate":
				logger.info("`locate` called by " + message.author.name)  # Event log
				await message.channel.send("This instance of "+VERSION+" is being run on **" + hostname + "**, IP address **" + socket.gethostbyname(hostname) + "**" +
														"\nLatency: " + str(int(client.latency // 1)) + "." + str(client.latency % 1)[2:5] + "s" +
														"\nUptime: " + self.get_uptime() + "." +
														"\nLast disconnect: " + str(self.last_disconnect)[0:16])

			# Kill command
			if message.content.startswith("kill"):
				logger.info("`kill` called by " + message.author.name)  # Event log

				reason = message.content[len("kill"):]
				death_note = "**" + self.user.name + " offline**\nReason for shutdown: " + reason

				await message.channel.send(death_note + "\n" + "Uptime: " + self.get_uptime() + ".")
				await client.close()


# Main body
if __name__ == "__main__":

	try:
		discord.TextChannel.create_thread = create_thread
		setup_config()
		intents = discord.Intents.all()
		intents.members = True
		client = MyClient(intents=intents)


		client.run(TOKEN)

	except Exception as exception:
		logger.error("Exception: " + str(exception) + "\n")  # Event log