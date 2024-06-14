import edge_tts

VOICE = "zh-CN-XiaoyiNeural"
OUTPUT_FILE = "../tts/test.mp3"


async def ttsTrans(content, OUT_FILE) -> None:
    """Main function"""
    communicate = edge_tts.Communicate(content, VOICE)
    await communicate.save(OUT_FILE)