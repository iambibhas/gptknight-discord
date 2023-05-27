# This example requires the 'message_content' intent.

import discord
import requests
import re
import os
from dotenv import dotenv_values
import time


config = dotenv_values(".env")

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

def openai_request(msg, num_try=1):
    r = requests.post("https://api.openai.com/v1/chat/completions", json={
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": msg}]
        }, headers={
            'Content-Type': "application/json",
            'Authorization': "Bearer {openai_token}".format(openai_token=config.get("OPENAI_TOKEN"))
    })

    response = r.json()
    if 'choices' in response:
        return response['choices'][0]['message']['content']
    else:
        print("Error in openai response")
        print(response)
        print("sleeping ", num_try, " seconds, and trying again")
        time.sleep(num_try)
        return openai_request(msg, num_try + 1)


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if re.search(r"(\d) (day|night)s? in (.+)", message.content.lower()):
        print(message)
        print(message.content)

        num, day_or_night, place = re.search(r"(\d) (day|night)s? in (.+)", message.content).groups()
        if len(place) > 12 or int(num) > 30:
            await message.reply("lol")
            return

        filename = "{place}-{num}-{dorn}.txt".format(place=place, num=num, dorn=day_or_night)
        if os.path.isfile(filename):
            with open(filename, 'r') as f:
                await message.reply(file=discord.File(f))
        else:
            content = openai_request(
                "write a travel itinerary for {place} for {num} {dorn}s".format(
                    place=place, num=num, dorn=day_or_night
                )
            )
            if content:
                with open(filename, 'w') as f:
                    f.write(content)

                with open(filename, 'r') as f:
                    await message.reply(file=discord.File(f))
            else:
                await message.reply("could not get a response. please try again.")
    elif message.content.lower().startswith("raw query"):
        print(message)
        print(message.content)

        msg = message.content.replace("raw query", "").strip()
        if msg:
            content = openai_request(msg)
            if content:
                await message.reply(content)
            else:
                await message.reply("could not get a response. please try again.")
        else:
            await message.reply("what is your query?")


client.run(config.get('DISCORD_BOT_TOKEN'))