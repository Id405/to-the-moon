#!/usr/bin/python
import requests
import json
import discord
import os
import asyncio

class ConfigurationError(Exception):
    '''Raised whenever there is an error in the users configuration'''

def write_config(config):
    with open('config.json', 'w') as file:
        json.dump(config, file, indent=4)

if not(os.path.isfile('config.json')):
    config = {
        'config': {
            'symbols': [
                'BTC',
                'ETH',
                'DOGE'
            ],
            'update_interval': 1
        },
        'database': {
            'messages': []
        },
        'token': ''
    }

    write_config(config)

config = {}

with open('config.json', 'r') as file:
    config = json.load(file)

if not(config['token']):
    raise ConfigurationError('No token supplied in config.json, please specify a token in the token field')

class MyClient(discord.Client):
    def build_status_embed(self):
        data = requests.get('http://api.coincap.io/v2/assets').json()
        embed = discord.Embed(title='Crypto Status')
        embed.set_thumbnail(url='https://freedesignfile.com/upload/2017/08/rocket-icon-vector.png')

        for crypto in data['data']:
            if(crypto['symbol'] in config['config']['symbols']):
                    embed.add_field(name=f"{crypto['symbol']}", value=f"{float(crypto['priceUsd']):.5g} USD ({float(crypto['changePercent24Hr']):.2f})%\n", inline=False)
        
        return embed
    
    async def send_oneshot_status(self, channel):
        return await channel.send('', embed=self.build_status_embed())
    
    async def query_message_id(self, id):
        for guild in self.guilds:
                    for channel in guild.channels:
                        try:
                            result = await channel.fetch_message(id)
                            return result
                        except (AttributeError, discord.errors.NotFound, discord.errors.Forbidden):
                            pass
        return None
    
    async def update_message_task(self):
        while not(self.is_closed()):
            for id in config['database']['messages']:
                message = await self.query_message_id(id)

                if(message == None):
                    print(f'could not update message {id}')
                    config['database']['messages'].remove(id)
                    write_config(config)
                    continue

                embed = self.build_status_embed()

                await message.edit(embed=embed)
            await asyncio.sleep(60 * config['config']['update_interval'])


    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))
        self.loop.create_task(self.update_message_task())

    async def on_message(self, message):
        if(message.content.startswith('.c')):
            split = message.content.split(' ')
            command = split[1]

            if command == "status":
                sentMessage = await self.send_oneshot_status(message.channel)

                if("update" in split):
                    config['database']['messages'].append(sentMessage.id)
                    write_config(config)

client = MyClient()
client.run(config['token'])