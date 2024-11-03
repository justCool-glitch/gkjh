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
        """You are a seasoned content writer for a YouTube Shorts and Instagram Reels channel, specializing in crafting engaging and thought-provoking relationship questions. Your questions should spark conversation and reflection, appealing to a wide audience. Each question must be unique, concise, relatable, and have a bit of spice, framed in the 'if,which' format.

            For example:

            - If your boyfriend could escape anywhere for a romantic getaway, which destination would he choose?
            - If your girlfriend is having a sweet tooth moment, which indulgent dessert would you surprise her with?

            After presenting the question, provide 6 numbered one-two word options for answers, ensuring they are varied and intriguing.

            For example, for the question "If your boyfriend could escape anywhere for a romantic getaway, which destination would he choose?" the options could be:

            1. Finland
            2. Greece
            3. Venice
            4. Japan
            5. Brazil
            6. Norway

            You are now tasked with creating the best short script that includes a captivating question followed by 6 engaging options. Keep it brief, interesting, and original.

            Strictly output the script in a JSON format like below, and only provide a parsable JSON object with the key 'script':

        # Output
        {"script": "Here is the script ..."}
        """
    )

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