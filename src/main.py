import gradio as gr
import logging
import os
from typing import Dict, List, Optional, Tuple
from audio.music_processor import MusicProcessor
from video.generator import VideoGenerator
from video.effects import ParticleSystem, GeometricPatterns, LightEffects
from models.text_to_script import ScriptGenerator
from models.visual_generator import VisualGenerator
import tempfile
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VideoCreator:
    def __init__(self):
        """Initialize the video creator with all necessary components."""
        load_dotenv()
        self.music_processor = MusicProcessor()
        self.video_generator = VideoGenerator()
        self.script_generator = ScriptGenerator()
        self.visual_generator = VisualGenerator()
        
    def create_music_video(self, audio_file: str, theme: str,
                         duration: Optional[float] = None) -> str:
        """Create a music-synchronized video.
        
        Args:
            audio_file (str): Path to the audio file
            theme (str): Visual theme to apply
            duration (float): Optional duration to trim to
            
        Returns:
            str: Path to the generated video
        """
        try:
            # Process audio
            audio_features = self.music_processor.process_audio_file(audio_file)
            
            if duration:
                # Trim audio if duration specified
                audio_file = self.music_processor.trim_audio(
                    audio_file, 0, duration
                )
                
            # Generate background video
            video_file = self.video_generator.generate_background(
                duration or audio_features['duration'],
                theme,
                audio_features
            )
            
            # Combine audio and video
            final_video = self.video_generator.combine_with_audio(
                video_file, audio_file
            )
            
            return final_video
        except Exception as e:
            logger.error(f"Error creating music video: {str(e)}")
            raise
            
    def create_tiktok_video(self, prompt: str, template: str = None,
                          duration: int = 60) -> str:
        """Create a TikTok-style video from a text prompt.
        
        Args:
            prompt (str): Text prompt describing the video
            template (str): Optional template name
            duration (int): Target duration in seconds
            
        Returns:
            str: Path to the generated video
        """
        try:
            # Generate script
            script_data = self.script_generator.generate_script(
                prompt, template, duration
            )
            
            # Generate visuals for each scene
            scene_videos = []
            for scene in script_data['script']:
                # Generate visual
                image_file = self.visual_generator.generate_scene_visuals(
                    scene,
                    style=template or 'realistic'
                )
                
                # Add text overlay if needed
                if scene['narration']:
                    image_file = self.visual_generator.create_text_overlay(
                        image_file,
                        scene['narration']
                    )
                    
                # Convert to video clip
                video_file = self._image_to_video(
                    image_file,
                    scene['duration']
                )
                
                scene_videos.append(video_file)
                
            # Combine scenes
            final_video = self._combine_scenes(scene_videos)
            
            # Generate hashtags
            hashtags = self.script_generator.suggest_hashtags(script_data)
            
            return final_video, hashtags
        except Exception as e:
            logger.error(f"Error creating TikTok video: {str(e)}")
            raise
            
    def _image_to_video(self, image_path: str, duration: float) -> str:
        """Convert an image to a video clip.
        
        Args:
            image_path (str): Path to the image
            duration (float): Duration in seconds
            
        Returns:
            str: Path to the video clip
        """
        try:
            # Create temporary file for video
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
            
            # Convert image to video (implementation needed)
            # This would typically use moviepy or similar library
            
            return temp_file.name
        except Exception as e:
            logger.error(f"Error converting image to video: {str(e)}")
            raise
            
    def _combine_scenes(self, video_files: List[str]) -> str:
        """Combine multiple video clips into one.
        
        Args:
            video_files (List[str]): List of video file paths
            
        Returns:
            str: Path to the combined video
        """
        try:
            # Create temporary file for combined video
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
            
            # Combine videos (implementation needed)
            # This would typically use moviepy or similar library
            
            return temp_file.name
        except Exception as e:
            logger.error(f"Error combining scenes: {str(e)}")
            raise

def create_ui():
    """Create the Gradio interface."""
    creator = VideoCreator()
    
    with gr.Blocks(title="AI Video Generator") as app:
        gr.Markdown("# AI Video Generator")
        
        with gr.Tabs():
            with gr.TabItem("Music Video Generator"):
                audio_input = gr.Audio(label="Upload Music")
                theme_input = gr.Dropdown(
                    choices=['realistic', 'animated', 'abstract', 'cinematic'],
                    label="Visual Theme"
                )
                duration_input = gr.Number(
                    label="Duration (seconds, optional)",
                    value=None
                )
                music_video_button = gr.Button("Generate Music Video")
                music_video_output = gr.Video(label="Generated Video")
                
                music_video_button.click(
                    creator.create_music_video,
                    inputs=[audio_input, theme_input, duration_input],
                    outputs=music_video_output
                )
                
            with gr.TabItem("TikTok Video Generator"):
                prompt_input = gr.Textbox(
                    label="Video Description",
                    placeholder="Describe your video..."
                )
                template_input = gr.Dropdown(
                    choices=['travel_vlog', 'product_demo'],
                    label="Template"
                )
                duration_input_tiktok = gr.Number(
                    label="Duration (seconds)",
                    value=60
                )
                tiktok_video_button = gr.Button("Generate TikTok Video")
                tiktok_video_output = gr.Video(label="Generated Video")
                hashtags_output = gr.Textbox(label="Suggested Hashtags")
                
                tiktok_video_button.click(
                    creator.create_tiktok_video,
                    inputs=[prompt_input, template_input, duration_input_tiktok],
                    outputs=[tiktok_video_output, hashtags_output]
                )
    
    return app

if __name__ == "__main__":
    app = create_ui()
    app.launch() 