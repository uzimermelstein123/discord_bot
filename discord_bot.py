import os
import discord
from dotenv import load_dotenv
from azure_ai import get_azure_ai_response  # Import the Azure AI function

# Load the bot token from the .env file
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Create a Discord client (bot) instance
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# Event listener for when the bot has connected and is ready
@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    for guild in client.guilds:
        print(f'- {guild.name} (id: {guild.id})')

# Event listener for when a message is sent
@client.event
async def on_message(message):
    # Prevent the bot from responding to its own messages
    if message.author == client.user:
        return

    if client.user.mentioned_in(message):
        if not message.mention_everyone:
            user_message = message.content.replace(f'<@{client.user.id}>', '').strip()
            print(f"User message: {user_message}")

            # Get response from Azure OpenAI
            response = get_azure_ai_response(user_message)
            await message.channel.send(response)

# Run the bot with your token
client.run(TOKEN)
