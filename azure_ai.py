import os
from openai import AzureOpenAI, OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
MODEL_API_KEY = os.getenv('MODEL_API_KEY')
AZURE_ENDPOINT = os.getenv('AZURE_ENDPOINT')  # Add this to your .env file
AZURE_DEPLOYMENT_NAME = os.getenv('AZURE_DEPLOYMENT_NAME')  # Add this to your .env file


client = OpenAI(
    base_url=AZURE_ENDPOINT,
    api_key=MODEL_API_KEY
)

def get_azure_ai_response(prompt: str) -> str:
    """
    Sends a prompt to Azure OpenAI and returns the response.
    """
    try:
 
        response = client.chat.completions.create(
            model=AZURE_DEPLOYMENT_NAME,  # The deployment name you set in Azure
            max_tokens=400, # Roughly 1,600 - 1,800 characters, Discord limits at 2k, I could split response but not for now
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        print(response.choices)
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"Error communicating with Azure OpenAI: {e}")
        return e