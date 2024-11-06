import edge_tts

async def generate_audio(text,outputFilename):
    communicate = edge_tts.Communicate(text=text,voice="en-AU-WilliamNeural",te="-20%",volume= "-10%",pitch="-10Hz")
    await communicate.save(outputFilename)





