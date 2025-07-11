from src.video_dubbing.crew import create_crew
import os

def run_dubbing(video_path: str) -> str:
    try:
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
        crew = create_crew()
        
        result = crew.kickoff(inputs={"video_path": video_path})
        if hasattr(result, 'raw'):
            output_path = result.raw.strip()
        else:
            output_path = str(result).strip()
        
        if not os.path.exists(output_path):
            raise FileNotFoundError(f"Dubbed video file not created: {output_path}")
        return output_path
        
    except Exception as e:
        print(f"Error in run_dubbing: {str(e)}")
        raise e