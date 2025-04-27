import fal_client
import os

def submit_musetalk_request(video_url, audio_url, api_key=None):
    if api_key is None:
        api_key = os.getenv("FAL_KEY")
    
    os.environ["FAL_KEY"] = api_key  # Set it so fal_client can find it

    arguments = {
        "source_video_url": video_url,
        "audio_url": audio_url
    }

    # Just call fal_client.run directly
    result = fal_client.run("fal-ai/musetalk", arguments=arguments)
    return result