from fal_client_wrapper import submit_musetalk_request
from input_data import get_input_data
from utils import log_result
from dotenv import load_dotenv

import os

load_dotenv() 
fal_key = os.getenv("FAL_KEY")

if not fal_key:
    raise ValueError("FAL_KEY is not set. Please check your .env file!")

def main():
    video_url, audio_url = get_input_data()
    result = submit_musetalk_request(video_url, audio_url, fal_key)
    print(result)
    log_result(result)

if __name__ == "__main__":
    main()