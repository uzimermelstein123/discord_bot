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
    print("Message")
    
    # Prevent the bot from responding to its own messages
    if message.author == client.user:
        print(f"{message.author} == {client.user}")
        return
    print(f"Client.user == {client.user}")
    print(f"Message. author= {message.author}")
    
    bot_name = f"@{client.user.name}"
    # print(bot_name)
    lowered_content = message.clean_content.lower()
    print(lowered_content)
    if client.user.name in lowered_content:
        print("Client mentioned")
        if not message.mention_everyone:
            # user_message = message.content.replace(f'<@{client.user.id}>', '').strip()
            prompt = lowered_content.replace(f"@{client.user.name}", "")
            
            print(f"User prompt: {prompt}") # This is where I will process prompt for CANVAS

            # Get response from Azure OpenAI
            response = get_azure_ai_response(prompt)
            # if isinstance(response, Exception): #interesting thought here to rerun code, for later
            #     print("An error occurred. Restarting the bot...")
            #     python = os.path.abspath(__file__)  # Get the current script's path
            #     os.execv(python, ["CTRL"] + ["C"])
            #     os.execv(python, ['python'] + [python])  # Restart the script
            # else:
            await message.channel.send(response)

# Run the bot with your token
if __name__ == "__main__":
    client.run(TOKEN)
