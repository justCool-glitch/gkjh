import os
from openai import OpenAI
import json

if len(os.environ.get("GROQ_API_KEY")) > 30:
    from groq import Groq
    model = "mixtral-8x7b-32768"
    client = Groq(
        api_key=os.environ.get("GROQ_API_KEY"),
        )
else:
    OPENAI_API_KEY = os.getenv('OPENAI_KEY')
    model = "gpt-4o"
    client = OpenAI(api_key=OPENAI_API_KEY)

def generate_script(topic):
    # Static JSON response to mimic the API's expected output
    static_response = {
        "script": f"{topic.capitalize()} facts you didn't know:\n"
                  "- Bananas are berries, but strawberries aren't.\n"
                  "- A single cloud can weigh over a million pounds.\n"
                  "- There's a species of jellyfish that is biologically immortal.\n"
                  "- Honey never spoils; archaeologists have found pots of honey in ancient Egyptian tombs that are over 3,000 years old and still edible.\n"
                  "- The shortest war in history was between Britain and Zanzibar on August 27, 1896. Zanzibar surrendered after 38 minutes.\n"
                  "- Octopuses have three hearts and blue blood."
    }
    
    # Return the "script" part of the static response
    return static_response["script"]
