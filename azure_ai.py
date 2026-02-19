import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
AZURE_API_KEY = os.getenv('AZURE_KEY')
AZURE_ENDPOINT = os.getenv('AZURE_ENDPOINT')  # Add this to your .env file
AZURE_DEPLOYMENT_NAME = os.getenv('AZURE_DEPLOYMENT_NAME')  # Add this to your .env file

# Configure OpenAI to use Azure
# openai.api_type = "azure"
# openai.api_key = AZURE_API_KEY
# openai.api_base = AZURE_ENDPOINT
# openai.api_version = "2023-03-15-preview"  # Update this if your Azure OpenAI version differs
client = OpenAI(
    # This is the default and can be omitted
    api_key=AZURE_API_KEY,
    api_base=AZURE_ENDPOINT,  # Corresponds to your Azure OpenAI endpoint
    api_type="azure",         # Specifies that this is an Azure OpenAI instance
    api_version="2023-03-15-preview"  # Update this if your Azure OpenAI version differs

)

def get_azure_ai_response(prompt: str) -> str:
    """
    Sends a prompt to Azure OpenAI and returns the response.
    """
    try:
        response = client.responses.create(
            model=AZURE_DEPLOYMENT_NAME,  # Corresponds to your Azure deployment name
            instructions="You are a discord assistant that talks to users and is helpful and gives honest feedback and advice.",
            input=prompt,  # Use the prompt provided by the user
        )
        # response = openai.ChatCompletion.create(
        #     engine=AZURE_DEPLOYMENT_NAME,  # The deployment name you set in Azure
        #     messages=[
        #         {"role": "system", "content": "You are a helpful assistant."},
        #         {"role": "user", "content": prompt}
        #     ]
        # )
        # return response['choices'][0]['message']['content']
        return response.output_text
    except Exception as e:
        print(f"Error communicating with Azure OpenAI: {e}")
        return "Sorry, I couldn't process that request."