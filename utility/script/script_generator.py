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
    model = "gpt-4o-mini"
    client = OpenAI(api_key=OPENAI_API_KEY)

def generate_script(topic):
    prompt = (
        """Write a three-line story filled with suspense and a sense of impending danger.
          Capture a moment where an everyday scene takes a sudden dark turn, leaving the reader with a lingering question or fear.
          Each line of the story should be in a new line

            Strictly output the script in a JSON format like below, and only provide a parsable JSON object with the key 'script':

        # Output
        {"script": "Here is the script ..."}  
         """
    )
    print("original prompt: "+prompt)
    response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": topic}
            ]
        )
    content = response.choices[0].message.content
    try:
        script = json.loads(content)["script"]
    except Exception as e:
        json_start_index = content.find('{')
        json_end_index = content.rfind('}')
        print(content)
        content = content[json_start_index:json_end_index+1]
        script = json.loads(content)["script"]
    return script