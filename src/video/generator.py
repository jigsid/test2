import cv2
import numpy as np
from typing import Dict, List, Tuple, Optional
import logging
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeVideoClip, ColorClip, ImageClip
import tempfile
import os
from PIL import Image, ImageDraw, ImageFilter
import random
import math

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VideoGenerator:
    def __init__(self, width: int = 1080, height: int = 1920):
        """Initialize the video generator with specified dimensions.
        
        Args:
            width (int): Width of the output video
            height (int): Height of the output video
        """
        self.width = width
        self.height = height
        self.fps = 30
        self.supported_themes = ['realistic', 'animated', 'abstract', 'cinematic']
        
    def generate_background(self, duration: float, theme: str,
                          audio_features: Dict[str, any]) -> str:
        """Generate a dynamic background video based on audio features.
        
        Args:
            duration (float): Duration of the video in seconds
            theme (str): Visual theme for the background
            audio_features (Dict): Dictionary containing audio analysis results
            
        Returns:
            str: Path to the generated video file
        """
        try:
            if theme.lower() not in self.supported_themes:
                raise ValueError(f"Unsupported theme. Supported themes: {self.supported_themes}")
            
            # Create base video clip
            base_clip = ColorClip((self.width, self.height), 
                                color=(0, 0, 0),
                                duration=duration)
            
            # Generate effects based on audio features
            effects = self._generate_effects(audio_features, theme)
            
            # Combine base clip with effects
            final_clip = CompositeVideoClip([base_clip] + effects)
            
            # Export video
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
            final_clip.write_videofile(temp_file.name, 
                                     fps=self.fps,
                                     codec='libx264',
                                     audio=False)
            
            return temp_file.name
        except Exception as e:
            logger.error(f"Error generating background video: {str(e)}")
            raise
            
    def _generate_effects(self, audio_features: Dict[str, any], 
                         theme: str) -> List[VideoFileClip]:
        """Generate visual effects based on audio features and theme.
        
        Args:
            audio_features (Dict): Dictionary containing audio analysis results
            theme (str): Visual theme for the effects
            
        Returns:
            List[VideoFileClip]: List of effect clips
        """
        effects = []
        
        # Get sync points and energy profile
        sync_points = audio_features['sync_points']
        energy_profile = audio_features['energy_profile']
        
        if theme.lower() == 'abstract':
            effects.extend(self._generate_abstract_effects(sync_points, energy_profile))
        elif theme.lower() == 'realistic':
            effects.extend(self._generate_realistic_effects(sync_points, energy_profile))
        elif theme.lower() == 'animated':
            effects.extend(self._generate_animated_effects(sync_points, energy_profile))
        elif theme.lower() == 'cinematic':
            effects.extend(self._generate_cinematic_effects(sync_points, energy_profile))
            
        return effects
        
    def _generate_abstract_effects(self, sync_points: List[Tuple[float, float]],
                                 energy_profile: np.ndarray) -> List[VideoFileClip]:
        """Generate abstract visual effects (e.g., geometric patterns, particles).
        
        Args:
            sync_points (List[Tuple]): List of (time, strength) tuples
            energy_profile (np.ndarray): Audio energy profile
            
        Returns:
            List[VideoFileClip]: List of abstract effect clips
        """
        effects = []
        
        # Generate particle system
        particles = self._create_particle_system(sync_points, energy_profile)
        effects.append(particles)
        
        # Generate geometric patterns
        patterns = self._create_geometric_patterns(sync_points, energy_profile)
        effects.append(patterns)
        
        return effects
        
    def _generate_realistic_effects(self, sync_points: List[Tuple[float, float]],
                                  energy_profile: np.ndarray) -> List[VideoFileClip]:
        """Generate realistic visual effects (e.g., light flares, bokeh).
        
        Args:
            sync_points (List[Tuple]): List of (time, strength) tuples
            energy_profile (np.ndarray): Audio energy profile
            
        Returns:
            List[VideoFileClip]: List of realistic effect clips
        """
        effects = []
        
        # Generate light flares
        flares = self._create_light_flares(sync_points)
        effects.append(flares)
        
        # Generate bokeh effects
        bokeh = self._create_bokeh_effects(energy_profile)
        effects.append(bokeh)
        
        return effects
        
    def _create_particle_system(self, sync_points: List[Tuple[float, float]],
                              energy_profile: np.ndarray) -> VideoFileClip:
        """Create a particle system animation synchronized with the music."""
        frames = []
        duration = len(energy_profile) / self.fps
        num_particles = 100
        particles = []

        # Initialize particles
        for _ in range(num_particles):
            particles.append({
                'x': random.randint(0, self.width),
                'y': random.randint(0, self.height),
                'size': random.randint(2, 8),
                'speed': random.uniform(2, 5),
                'angle': random.uniform(0, 2 * math.pi)
            })

        # Create frames
        for i in range(int(duration * self.fps)):
            frame = np.zeros((self.height, self.width, 4), dtype=np.uint8)
            energy = energy_profile[min(i, len(energy_profile) - 1)]

            # Update and draw particles
            for particle in particles:
                # Update position based on energy
                particle['x'] += math.cos(particle['angle']) * particle['speed'] * energy
                particle['y'] += math.sin(particle['angle']) * particle['speed'] * energy

                # Wrap around screen
                particle['x'] = particle['x'] % self.width
                particle['y'] = particle['y'] % self.height

                # Draw particle
                size = int(particle['size'] * (1 + energy))
                cv2.circle(frame, 
                         (int(particle['x']), int(particle['y'])), 
                         size,
                         (255, 255, 255, int(255 * energy)),
                         -1)

                # Change direction slightly
                particle['angle'] += random.uniform(-0.1, 0.1)

            frames.append(frame)

        # Convert frames to video clip
        clip = ImageClip(frames[0]).set_duration(duration)
        clip = clip.set_position(('center', 'center'))
        return clip

    def _create_geometric_patterns(self, sync_points: List[Tuple[float, float]],
                                 energy_profile: np.ndarray) -> VideoFileClip:
        """Create geometric pattern animations synchronized with the music."""
        frames = []
        duration = len(energy_profile) / self.fps
        pattern_types = ['circles', 'triangles', 'squares']
        current_pattern = 0

        for i in range(int(duration * self.fps)):
            frame = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
            draw = ImageDraw.Draw(frame)
            energy = energy_profile[min(i, len(energy_profile) - 1)]

            # Change pattern on strong beats
            for time, strength in sync_points:
                if abs(time - i/self.fps) < 0.1:
                    current_pattern = (current_pattern + 1) % len(pattern_types)

            # Draw patterns based on energy
            if pattern_types[current_pattern] == 'circles':
                num_circles = int(10 * energy)
                for _ in range(num_circles):
                    size = random.randint(50, 200)
                    x = random.randint(-size, self.width + size)
                    y = random.randint(-size, self.height + size)
                    draw.ellipse([x-size, y-size, x+size, y+size],
                               outline=(255, 255, 255, int(255 * energy)))

            elif pattern_types[current_pattern] == 'triangles':
                num_triangles = int(8 * energy)
                for _ in range(num_triangles):
                    size = random.randint(50, 150)
                    x = random.randint(0, self.width)
                    y = random.randint(0, self.height)
                    points = [
                        (x, y-size),
                        (x-size, y+size),
                        (x+size, y+size)
                    ]
                    draw.polygon(points, outline=(255, 255, 255, int(255 * energy)))

            else:  # squares
                num_squares = int(6 * energy)
                for _ in range(num_squares):
                    size = random.randint(40, 120)
                    x = random.randint(-size, self.width + size)
                    y = random.randint(-size, self.height + size)
                    draw.rectangle([x-size, y-size, x+size, y+size],
                                 outline=(255, 255, 255, int(255 * energy)))

            frames.append(np.array(frame))

        clip = ImageClip(frames[0]).set_duration(duration)
        clip = clip.set_position(('center', 'center'))
        return clip

    def _create_light_flares(self, sync_points: List[Tuple[float, float]]) -> VideoFileClip:
        """Create light flare effects synchronized with strong beats."""
        frames = []
        duration = sync_points[-1][0] if sync_points else 5.0
        
        for i in range(int(duration * self.fps)):
            frame = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
            current_time = i / self.fps

            # Check for nearby sync points
            for time, strength in sync_points:
                time_diff = abs(current_time - time)
                if time_diff < 0.1:  # Within 100ms of beat
                    # Create light flare
                    flare_size = int(500 * strength)
                    x = random.randint(0, self.width)
                    y = random.randint(0, self.height)
                    
                    # Create radial gradient
                    for radius in range(flare_size, 0, -2):
                        opacity = int(255 * (1 - time_diff*10) * (radius/flare_size) * strength)
                        ImageDraw.Draw(frame).ellipse(
                            [x-radius, y-radius, x+radius, y+radius],
                            fill=(255, 255, 255, opacity)
                        )
                    
                    # Add lens streaks
                    for angle in range(0, 360, 45):
                        streak_length = random.randint(100, 300)
                        end_x = x + streak_length * math.cos(math.radians(angle))
                        end_y = y + streak_length * math.sin(math.radians(angle))
                        ImageDraw.Draw(frame).line(
                            [x, y, end_x, end_y],
                            fill=(255, 255, 255, int(127 * strength)),
                            width=2
                        )

            # Apply gaussian blur
            frame = frame.filter(ImageFilter.GaussianBlur(radius=5))
            frames.append(np.array(frame))

        clip = ImageClip(frames[0]).set_duration(duration)
        clip = clip.set_position(('center', 'center'))
        return clip

    def _create_bokeh_effects(self, energy_profile: np.ndarray) -> VideoFileClip:
        """Create bokeh effects that respond to audio energy."""
        frames = []
        duration = len(energy_profile) / self.fps
        bokeh_points = []

        # Initialize bokeh points
        for _ in range(30):
            bokeh_points.append({
                'x': random.randint(0, self.width),
                'y': random.randint(0, self.height),
                'size': random.randint(20, 100),
                'color': (
                    random.randint(200, 255),
                    random.randint(200, 255),
                    random.randint(200, 255)
                )
            })

        for i in range(int(duration * self.fps)):
            frame = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
            energy = energy_profile[min(i, len(energy_profile) - 1)]

            # Draw and update bokeh points
            for point in bokeh_points:
                # Scale size with energy
                current_size = int(point['size'] * (0.5 + energy))
                
                # Create bokeh circle
                bokeh = Image.new('RGBA', (current_size*2, current_size*2), (0, 0, 0, 0))
                draw = ImageDraw.Draw(bokeh)
                
                # Draw gradient circle
                for radius in range(current_size, 0, -1):
                    opacity = int(255 * (radius/current_size) * 0.5)
                    color = tuple(list(point['color']) + [opacity])
                    draw.ellipse([current_size-radius, current_size-radius,
                                current_size+radius, current_size+radius],
                               fill=color)

                # Apply gaussian blur
                bokeh = bokeh.filter(ImageFilter.GaussianBlur(radius=3))
                
                # Paste bokeh onto frame
                frame.paste(bokeh, (int(point['x']-current_size),
                                  int(point['y']-current_size)),
                          bokeh)

                # Move points slowly
                point['x'] += random.uniform(-1, 1)
                point['y'] += random.uniform(-1, 1)

                # Wrap around screen
                point['x'] = point['x'] % self.width
                point['y'] = point['y'] % self.height

            frames.append(np.array(frame))

        clip = ImageClip(frames[0]).set_duration(duration)
        clip = clip.set_position(('center', 'center'))
        return clip
        
    def combine_with_audio(self, video_path: str, audio_path: str) -> str:
        """Combine video with audio track.
        
        Args:
            video_path (str): Path to the video file
            audio_path (str): Path to the audio file
            
        Returns:
            str: Path to the combined video file
        """
        try:
            # Load video and audio
            video = VideoFileClip(video_path)
            audio = AudioFileClip(audio_path)
            
            # Set audio
            final_video = video.set_audio(audio)
            
            # Export combined video
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
            final_video.write_videofile(temp_file.name,
                                      fps=self.fps,
                                      codec='libx264')
            
            return temp_file.name
        except Exception as e:
            logger.error(f"Error combining video and audio: {str(e)}")
            raise
            
    def apply_effects(self, video_path: str, effects: List[Dict[str, any]]) -> str:
        """Apply post-processing effects to the video.
        
        Args:
            video_path (str): Path to the video file
            effects (List[Dict]): List of effect configurations
            
        Returns:
            str: Path to the processed video file
        """
        try:
            # Load video
            video = VideoFileClip(video_path)
            
            # Apply each effect
            for effect in effects:
                if effect['type'] == 'color_grading':
                    video = self._apply_color_grading(video, effect['params'])
                elif effect['type'] == 'blur':
                    video = self._apply_blur(video, effect['params'])
                # Add more effect types as needed
            
            # Export processed video
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
            video.write_videofile(temp_file.name,
                                fps=self.fps,
                                codec='libx264')
            
            return temp_file.name
        except Exception as e:
            logger.error(f"Error applying effects: {str(e)}")
            raise
            
    def _apply_color_grading(self, video: VideoFileClip, 
                           params: Dict[str, float]) -> VideoFileClip:
        """Apply color grading to the video.
        
        Args:
            video (VideoFileClip): Input video
            params (Dict): Color grading parameters
            
        Returns:
            VideoFileClip: Color graded video
        """
        # Implementation for color grading
        # This is a placeholder - actual implementation would apply
        # color grading based on provided parameters
        pass
        
    def _apply_blur(self, video: VideoFileClip, 
                   params: Dict[str, float]) -> VideoFileClip:
        """Apply blur effect to the video.
        
        Args:
            video (VideoFileClip): Input video
            params (Dict): Blur parameters
            
        Returns:
            VideoFileClip: Blurred video
        """
        # Implementation for blur effect
        # This is a placeholder - actual implementation would apply
        # blur effect based on provided parameters
        pass 