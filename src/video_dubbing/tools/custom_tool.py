__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
sys.modules["sqlite3.dbapi2"] = sys.modules["pysqlite3.dbapi2"]

from crewai.tools import tool
import os
import requests
from pathlib import Path
import time
import json

@tool("ElevenLabs Dubbing Tool")
def dub_english_to_hindi(video_path: str) -> str:
    """Dubs an English video to Hindi using ElevenLabs Dubbing API and returns the new video path."""

    print(f"[Tool] Starting dubbing for: {video_path}")

    eleven_api_key = os.getenv("ELEVENLABS_API_KEY")
    if not eleven_api_key:
        raise Exception("Missing ELEVENLABS_API_KEY in environment variables")

    url = "https://api.elevenlabs.io/v1/dubbing"

    # Upload video file
    with open(video_path, "rb") as video_file:
        files = {
            "file": (Path(video_path).name, video_file, "video/mp4")
        }
        data = {
            "source_lang": "en",
            "target_lang": "hi",
            "watermark": "true"
        }
        headers = {
            "xi-api-key": eleven_api_key
        }

        print("[Tool] Uploading video for dubbing...")
        response = requests.post(url, headers=headers, data=data, files=files)

    if response.status_code != 200:
        try:
            error_detail = response.json()
            print(f"[Tool] API Error Response: {json.dumps(error_detail, indent=2)}")
        except:
            print(f"[Tool] API Error Response: {response.text}")
        raise Exception(f"[Dubbing API] Failed: {response.status_code} - {response.text}")

    # Get the dubbing ID from response
    try:
        response_data = response.json()
    except Exception as e:
        print(f"[Tool] Failed to parse JSON response: {response.text}")
        raise Exception(f"[Dubbing API] Invalid JSON response: {e}")
    
    dubbing_id = response_data.get("dubbing_id")
    
    if not dubbing_id:
        raise Exception(f"[Dubbing API] No dubbing_id in response: {response_data}")

    print(f"[Tool] Dubbing started with ID: {dubbing_id}")
    
    # Poll for completion
    status_url = f"https://api.elevenlabs.io/v1/dubbing/{dubbing_id}"
    
    while True:
        print("[Tool] Checking dubbing status...")
        status_response = requests.get(status_url, headers=headers)
        
        if status_response.status_code != 200:
            try:
                error_detail = status_response.json()
                print(f"[Tool] Status API Error Response: {json.dumps(error_detail, indent=2)}")
            except:
                print(f"[Tool] Status API Error Response: {status_response.text}")
            raise Exception(f"[Status API] Failed: {status_response.status_code} - {status_response.text}")
        
        try:
            status_data = status_response.json()
        except Exception as e:
            print(f"[Tool] Failed to parse status JSON response: {status_response.text}")
            raise Exception(f"[Status API] Invalid JSON response: {e}")
        
        if not isinstance(status_data, dict):
            print(f"[Tool] Status response is not a dict: {status_data}")
            raise Exception(f"[Status API] Unexpected response format: {status_data}")
        
        status = status_data.get("status")
        
        print(f"[Tool] Dubbing status: {status}")
        
        if status == "dubbed":
            break
        elif status == "failed":
            error_msg = status_data.get("error", "Unknown error")
            raise Exception(f"[Dubbing] Failed: {error_msg}")
        
        # Wait before next check
        time.sleep(10)  # Increased wait time to avoid rate limiting
    
    # Download the dubbed video using the correct endpoint
    print("[Tool] Downloading dubbed video...")
    download_url = f"https://api.elevenlabs.io/v1/dubbing/{dubbing_id}/audio/hi"
    
    download_response = requests.get(download_url, headers=headers)
    
    if download_response.status_code != 200:
        try:
            error_detail = download_response.json()
            print(f"[Tool] Download API Error Response: {json.dumps(error_detail, indent=2)}")
        except:
            print(f"[Tool] Download API Error Response: {download_response.text}")
        raise Exception(f"[Download API] Failed: {download_response.status_code} - {download_response.text}")
    
    # Save output video
    dubbed_output_path = Path(video_path).with_name("dubbed_hindi_video.mp4")
    with open(dubbed_output_path, "wb") as f:
        f.write(download_response.content)

    print(f"[Tool] Dubbed video created: {dubbed_output_path}")
    return str(dubbed_output_path)