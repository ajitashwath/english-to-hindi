__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
sys.modules["sqlite3.dbapi2"] = sys.modules["pysqlite3.dbapi2"]

import streamlit as st
import tempfile
import os
from src.video_dubbing.main import run_dubbing

st.set_page_config(page_title="English to Hindi Video Dubber", layout="centered")
st.title("🎬 English to Hindi Video Dubber")

api_key = st.text_input("Enter your OpenAI API Key", type="password")
if api_key:
    os.environ["OPENAI_API_KEY"] = api_key

video_file = st.file_uploader("Upload English video (mp4)", type=["mp4"])

if st.button("Start Dubbing"):
    if not api_key:
        st.error("Please enter your OpenAI API Key.")
    elif not video_file:
        st.error("Please upload a video file.")
    else:
        with st.spinner("Processing... please wait a moment."):
            try:
                temp_video_path = tempfile.mktemp(suffix=".mp4")
                with open(temp_video_path, "wb") as f:
                    f.write(video_file.read())
                dubbed_video_path = run_dubbing(temp_video_path)
                
                if dubbed_video_path and os.path.exists(dubbed_video_path):
                    st.success("Hindi dubbed video generated!")
                    st.video(dubbed_video_path)
                    with open(dubbed_video_path, "rb") as f:
                        st.download_button(
                            label="Download Dubbed Video",
                            data=f.read(),
                            file_name="dubbed_hindi_video.mp4",
                            mime="video/mp4"
                        )
                else:
                    st.error("Failed to generate dubbed video.")
                    
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
            finally:
                if 'temp_video_path' in locals() and os.path.exists(temp_video_path):
                    os.remove(temp_video_path)