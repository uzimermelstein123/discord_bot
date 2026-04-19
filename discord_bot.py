import os
import discord
from dotenv import load_dotenv
from azure_ai import get_azure_ai_response
from assignment_time_pipeline import estimate_assignment_time

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
    
    lowered_content = message.clean_content.lower()
    if client.user.name.lower() in lowered_content:
        print("Client mentioned")
        if not message.mention_everyone:
            prompt = message.clean_content.replace(f"@{client.user.name}", "").strip()

            print(f"User prompt: {prompt}")

            prompt_lower = prompt.lower()
            if "how long" in prompt_lower and ("take" in prompt_lower or "will" in prompt_lower):
                # Strip command words to extract assignment name
                assignment_query = (
                    prompt_lower
                    .replace("how long will", "")
                    .replace("how long does", "")
                    .replace("how long", "")
                    .replace("take", "")
                    .replace("?", "")
                    .strip()
                )
                print(f"Assignment time query: {assignment_query}")
                response = estimate_assignment_time(assignment_query)
            else:
                response = get_azure_ai_response(prompt)

            await message.channel.send(response)

# Run the bot with your token
if __name__ == "__main__":
    client.run(TOKEN)
