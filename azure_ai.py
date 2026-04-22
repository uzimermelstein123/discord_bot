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

def get_assignment_time_estimate(assignment_name: str, course_name: str, context: str) -> str:
    """
    Estimates how long an assignment will take based on its stored content.
    """
    system_prompt = (
        "You are an academic assistant that helps students plan their time. "
        "Given assignment details, estimate realistically how long it will take to complete. "
        "Break the estimate down by task (reading, writing, coding, problem-solving, etc.). "
        "Be concise — your full response must fit within 1800 characters."
    )
    user_prompt = (
        f"Course: {course_name}\n"
        f"Assignment: {assignment_name}\n\n"
        f"Assignment content:\n{context}\n\n"
        "How long will this assignment take to complete? Give a time breakdown by task."
    )
    try:
        response = client.chat.completions.create(
            model=AZURE_DEPLOYMENT_NAME,
            max_tokens=500,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        print(response.choices[0].message.content)
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error communicating with Azure OpenAI: {e}")
        return "Sorry, I encountered an error estimating the assignment time."


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