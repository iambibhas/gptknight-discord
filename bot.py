# This example requires the 'message_content' intent.

import discord
import requests
import re
import os
from dotenv import dotenv_values


config = dotenv_values(".env")

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    print(message)
    print(message.content)

    if re.search(r"(\d) (day|night)s? in (.+)", message.content):
        # curl https://api.openai.com/v1/chat/completions   -H 'Content-Type: application/json'   -H 'Authorization: Bearer <foo>'   -d '{
        #   "model": "gpt-3.5-turbo",
        #   "messages": [{"role": "user", "content": "write a travel itinerary for wayanad for 3 nights"}]
        # }'
        num, day_or_night, place = re.search(r"(\d) (day|night)s? in (.+)", message.content).groups()
        if len(place) > 12 or int(num) > 30:
            await message.channel.send("lol")
            return

        filename = "{place}-{num}-{dorn}.txt".format(place=place, num=num, dorn=day_or_night)
        if os.path.isfile(filename):
            with open(filename, 'r') as f:
                await message.channel.send(file=discord.File(f))
        else:
            r = requests.post("https://api.openai.com/v1/chat/completions", json={
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": "write a travel itinerary for {place} for {num} {dorn}s".format(place=place, num=num, dorn=day_or_night)}]
            }, headers={
                'Content-Type': "application/json",
                'Authorization': "Bearer {openai_token}".format(openai_token=config.get("OPENAI_TOKEN"))
            })

            response = r.json()
            if 'choices' in response:
                content = response['choices'][0]['message']['content']
                with open(filename, 'w') as f:
                    f.write(content)

                with open(filename, 'r') as f:
                    await message.channel.send(file=discord.File(f))
            else:
                print(response)
                await message.channel.send("could not get a response. please try again.")


client.run(config.get('DISCORD_BOT_TOKEN'))