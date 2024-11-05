import whisper_timestamped as whisper
from whisper_timestamped import load_model, transcribe_timestamped
import re

def generate_timed_captions(audio_filename,model_size="base"):
    WHISPER_MODEL = load_model(model_size)
   
    gen = transcribe_timestamped(WHISPER_MODEL, audio_filename, verbose=False, fp16=False)
   
    return getCaptionsWithTime(gen)

def splitWordsBySize(words, maxCaptionSize):
   
    halfCaptionSize = maxCaptionSize / 2
    captions = []
    while words:
        caption = words[0]
        words = words[1:]
        while words and len(caption + ' ' + words[0]) <= maxCaptionSize:
            caption += ' ' + words[0]
            words = words[1:]
            if len(caption) >= halfCaptionSize and words:
                break
        captions.append(caption)
    return captions

def getTimestampMapping(whisper_analysis):
   
    index = 0
    locationToTimestamp = {}
    for segment in whisper_analysis['segments']:
        for word in segment['words']:
            newIndex = index + len(word['text'])+1
            locationToTimestamp[(index, newIndex)] = word['end']
            index = newIndex
    return locationToTimestamp

def cleanWord(word):
   
    return re.sub(r'[^\w\s\-_"\'\']', '', word)

def interpolateTimeFromDict(word_position, d):
   
    for key, value in d.items():
        if key[0] <= word_position <= key[1]:
            return value
    return None

# def getCaptionsWithTime(whisper_analysis, maxCaptionSize=15, considerPunctuation=False):
   
#     wordLocationToTime = getTimestampMapping(whisper_analysis)
#     position = 0
#     start_time = 0
#     CaptionsPairs = []
#     text = whisper_analysis['text']
    
#     if considerPunctuation:
#         sentences = re.split(r'(?<=[.!?]) +', text)
#         words = [word for sentence in sentences for word in splitWordsBySize(sentence.split(), maxCaptionSize)]
#     else:
#         words = text.split()
#         words = [cleanWord(word) for word in splitWordsBySize(words, maxCaptionSize)]
    
#     for word in words:
#         position += len(word) + 1
#         end_time = interpolateTimeFromDict(position, wordLocationToTime)
#         if end_time and word:
#             CaptionsPairs.append(((start_time, end_time), word))
#             start_time = end_time

#     return CaptionsPairs

def getCaptionsWithTime(whisper_analysis, considerPunctuation=False):
    # Generate a mapping from character position to timestamp
    wordLocationToTime = getTimestampMapping(whisper_analysis)
    start_time = 0
    CaptionsPairs = []
    text = whisper_analysis['text']
    
    # Split the text based on newlines to create individual caption lines
    if considerPunctuation:
        # Split by punctuation and keep sentences on separate lines
        lines = re.split(r'(?<=[.!?])\n*', text)
    else:
        # Split by newlines
        lines = text.split('\n')
    
    position = 0
    
    for line in lines:
        # Only process non-empty lines
        if line.strip():
            # Calculate the new position after the current line
            position += len(line) + 1  # assuming '\n' takes 1 character space
            end_time = interpolateTimeFromDict(position, wordLocationToTime)
            
            # Append the start and end time along with the line to CaptionsPairs
            if end_time:
                CaptionsPairs.append(((start_time, end_time), line))
                start_time = end_time  # Update start_time for the next line
            
    return CaptionsPairs
