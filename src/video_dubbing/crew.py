import os
from crewai import Agent, Task, Crew, Process
from src.video_dubbing.tools.custom_tool import dub_english_to_hindi
from dotenv import load_dotenv

def create_crew():
    load_dotenv()
    
    dubber_agent = Agent(
        role="Video Dubber",
        goal="Dub English videos into Hindi efficiently and accurately",
        backstory=(
            "You are an expert in media translation and dubbing, specializing in "
            "converting English video content to Hindi. You use advanced AI tools "
            "to transcribe, translate, and generate dubbed content with high quality."
        ),
        tools=[dub_english_to_hindi],
        verbose=True,
        allow_delegation=False
    )
    
    dubbing_task = Task(
        description=(
            "Process the provided English video file to create a Hindi dubbed version. "
            "Follow these steps:\n"
            "1. Transcribe the English audio from the video\n"
            "2. Translate the transcription to Hindi\n"
            "3. Generate Hindi speech from the translation\n"
            "4. Replace the original audio with the Hindi audio\n"
            "5. Output the final dubbed video file\n\n"
            "Video file path: {video_path}\n\n"
            "Ensure the final output is a complete video file with Hindi audio "
            "that maintains the original video quality."
        ),
        expected_output=(
            "The complete file path to the Hindi dubbed video file. "
            "The video should have the original visual content with Hindi audio dubbing."
        ),
        agent=dubber_agent,
    )
    
    return Crew(
        agents=[dubber_agent],
        tasks=[dubbing_task],
        process=Process.sequential,
        verbose=True
    )