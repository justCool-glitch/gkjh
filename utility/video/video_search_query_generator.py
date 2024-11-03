from openai import OpenAI
import os
import json
import re
from datetime import datetime
from utility.utils import log_response,LOG_TYPE_GPT

if len(os.environ.get("GROQ_API_KEY")) > 30:
    from groq import Groq
    model = "llama3-70b-8192"
    client = Groq(
        api_key=os.environ.get("GROQ_API_KEY"),
        )
else:
    model = "gpt-4o"
    OPENAI_API_KEY = os.environ.get('OPENAI_KEY')
    client = OpenAI(api_key=OPENAI_API_KEY)

log_directory = ".logs/gpt_logs"

prompt = """# Instructions

Given the following video script and timed captions, extract three visually concrete and specific keywords for each time segment that can be used to search for background videos. The keywords should be short and capture the main essence of the sentence. They can be synonyms or related terms. If a caption is vague or general, consider the next timed caption for more context. If a keyword is a single word, try to return a two-word keyword that is visually concrete. If a time frame contains two or more important pieces of information, divide it into shorter time frames with one keyword each. Ensure that the time periods are strictly consecutive and cover the entire length of the video. Each keyword should cover between 2-4 seconds. The output should be in JSON format, like this: [[[t1, t2], ["keyword1", "keyword2", "keyword3"]], [[t2, t3], ["keyword4", "keyword5", "keyword6"]], ...]. Please handle all edge cases, such as overlapping time segments, vague or general captions, and single-word keywords.

For example, if the caption is 'The cheetah is the fastest land animal, capable of running at speeds up to 75 mph', the keywords should include 'cheetah running', 'fastest animal', and '75 mph'. Similarly, for 'The Great Wall of China is one of the most iconic landmarks in the world', the keywords should be 'Great Wall of China', 'iconic landmark', and 'China landmark'.

Important Guidelines:

Use only English in your text queries.
Each search string must depict something visual.
The depictions have to be extremely visually concrete, like rainy street, or cat sleeping.
'emotional moment' <= BAD, because it doesn't depict something visually.
'crying child' <= GOOD, because it depicts something visual.
The list must always contain the most relevant and appropriate query searches.
['Car', 'Car driving', 'Car racing', 'Car parked'] <= BAD, because it's 4 strings.
['Fast car'] <= GOOD, because it's 1 string.
['Un chien', 'une voiture rapide', 'une maison rouge'] <= BAD, because the text query is NOT in English.

Note: Your response should be the response only and no extra text or data.
  """

def fix_json(json_str):
    # Replace typographical apostrophes with straight quotes
    json_str = json_str.replace("’", "'")
    # Replace any incorrect quotes (e.g., mixed single and double quotes)
    json_str = json_str.replace("“", "\"").replace("”", "\"").replace("‘", "\"").replace("’", "\"")
    # Add escaping for quotes within the strings
    json_str = json_str.replace('"you didn"t"', '"you didn\'t"')
    return json_str

def getVideoSearchQueriesTimed(script, captions_timed):
    end = captions_timed[-1][0][1]
    try:
        print("inside try for getVideoSearchQueriesTimed")
        out = [[[0, 0], ""]]
        
        # Loop until the end time matches the last segment's end time
        while out[-1][0][1] != end:
            content = call_OpenAI(script, captions_timed).replace("'", '"')
            print("got content", content)
            
            try:
                print("trying to load json")
                out = json.loads(content)
                
                # Check if the last segment's end time matches 'end'
                if out[-1][0][1] != end:
                    print(f"The current output end time ({out[-1][0][1]}) does not match the expected end time ({end}). Retrying...")

            except Exception as e:
                print("error in json load", e)
                print("content: \n", content, "\n\n")
                content = fix_json(content.replace("```json", "").replace("```", ""))
                
                # Retry parsing after fixing the JSON content
                out = json.loads(content)
        
        print("returning out", out)
        return out

    except Exception as e:
        print("error in response", e)
   
    return None

def call_OpenAI(script, captions_timed):
    # Static response that mimics expected output with keywords for each time segment
    static_response = """
    [
        [[0, 2], ["bananas berries", "strawberries not berries", "fruit facts"]],
        [[2, 4], ["heavy cloud", "million pounds cloud", "cloud weight"]],
        [[4, 6], ["immortal jellyfish", "unique species", "biological immortality"]],
        [[6, 8], ["ancient honey", "Egyptian tomb", "3,000-year-old honey"]],
        [[8, 10], ["shortest war", "Britain Zanzibar war", "38-minute war"]],
        [[10, 31.5], ["octopus hearts", "blue blood", "three hearts"]]
    ]
    """
    
    # Return the static response formatted as JSON
    return static_response.strip()


def merge_empty_intervals(segments):
    merged = []
    i = 0
    while i < len(segments):
        interval, url = segments[i]
        if url is None:
            # Find consecutive None intervals
            j = i + 1
            while j < len(segments) and segments[j][1] is None:
                j += 1
            
            # Merge consecutive None intervals with the previous valid URL
            if i > 0:
                prev_interval, prev_url = merged[-1]
                if prev_url is not None and prev_interval[1] == interval[0]:
                    merged[-1] = [[prev_interval[0], segments[j-1][0][1]], prev_url]
                else:
                    merged.append([interval, prev_url])
            else:
                merged.append([interval, None])
            
            i = j
        else:
            merged.append([interval, url])
            i += 1
    
    return merged
