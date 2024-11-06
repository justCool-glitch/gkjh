import edge_tts

async def generate_audio(text,outputFilename):
    communicate = edge_tts.Communicate(text=text,voice="en-AU-WilliamNeural",rate="-20%",volume= "-10%",pitch="-10Hz")
    await communicate.save(outputFilename)





