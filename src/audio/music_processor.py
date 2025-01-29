import os
import numpy as np
from typing import Dict, List, Optional, Tuple
import logging
from .beat_detection import BeatDetector
from pydub import AudioSegment
import tempfile

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MusicProcessor:
    def __init__(self):
        """Initialize the music processor with beat detection capabilities."""
        self.beat_detector = BeatDetector()
        self.supported_formats = ['.mp3', '.wav', '.m4a', '.ogg']
        
    def process_audio_file(self, file_path: str) -> Dict[str, any]:
        """Process an audio file and extract all necessary features for video generation.
        
        Args:
            file_path (str): Path to the audio file
            
        Returns:
            Dictionary containing all extracted features and analysis results
        """
        try:
            # Validate file format
            if not self._validate_audio_file(file_path):
                raise ValueError(f"Unsupported audio format. Supported formats: {self.supported_formats}")
            
            # Load and analyze audio
            y, sr = self.beat_detector.load_audio(file_path)
            
            # Get basic beat information
            beat_info = self.beat_detector.detect_beats(y, sr)
            
            # Get additional rhythm features
            rhythm_features = self.beat_detector.analyze_rhythm_features(y, sr)
            
            # Get sync points for strong beats
            sync_points = self.beat_detector.get_sync_points(
                beat_info['beat_times'],
                beat_info['beat_strengths']
            )
            
            # Get section information
            sections = self.beat_detector.get_sections(y, sr)
            
            # Calculate energy profile
            energy_profile = self._calculate_energy_profile(y)
            
            return {
                'beat_info': beat_info,
                'rhythm_features': rhythm_features,
                'sync_points': sync_points,
                'sections': sections,
                'energy_profile': energy_profile,
                'duration': len(y) / sr,
                'sample_rate': sr
            }
        except Exception as e:
            logger.error(f"Error processing audio file: {str(e)}")
            raise
            
    def _validate_audio_file(self, file_path: str) -> bool:
        """Validate if the audio file format is supported.
        
        Args:
            file_path (str): Path to the audio file
            
        Returns:
            bool: True if format is supported, False otherwise
        """
        _, ext = os.path.splitext(file_path.lower())
        return ext in self.supported_formats
        
    def _calculate_energy_profile(self, y: np.ndarray, 
                                frame_length: int = 2048,
                                hop_length: int = 512) -> np.ndarray:
        """Calculate the energy profile of the audio signal.
        
        Args:
            y (np.ndarray): Audio time series
            frame_length (int): Length of each frame
            hop_length (int): Number of samples between frames
            
        Returns:
            np.ndarray: Energy profile of the signal
        """
        # Calculate RMS energy for each frame
        energy = np.array([
            np.sqrt(np.mean(frame**2))
            for frame in self._frame_signal(y, frame_length, hop_length)
        ])
        
        # Normalize energy
        energy = (energy - energy.min()) / (energy.max() - energy.min())
        
        return energy
        
    def _frame_signal(self, y: np.ndarray, frame_length: int, 
                     hop_length: int) -> np.ndarray:
        """Frame the signal into overlapping frames.
        
        Args:
            y (np.ndarray): Audio time series
            frame_length (int): Length of each frame
            hop_length (int): Number of samples between frames
            
        Returns:
            np.ndarray: Framed signal
        """
        n_frames = 1 + (len(y) - frame_length) // hop_length
        frames = np.zeros((n_frames, frame_length))
        
        for i in range(n_frames):
            frames[i] = y[i * hop_length:i * hop_length + frame_length]
            
        return frames
        
    def trim_audio(self, file_path: str, start_time: float, 
                  end_time: float) -> str:
        """Trim audio file to specified duration.
        
        Args:
            file_path (str): Path to the audio file
            start_time (float): Start time in seconds
            end_time (float): End time in seconds
            
        Returns:
            str: Path to the trimmed audio file
        """
        try:
            # Load audio file
            audio = AudioSegment.from_file(file_path)
            
            # Convert times to milliseconds
            start_ms = int(start_time * 1000)
            end_ms = int(end_time * 1000)
            
            # Trim audio
            trimmed_audio = audio[start_ms:end_ms]
            
            # Create temporary file for trimmed audio
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
            trimmed_audio.export(temp_file.name, format='mp3')
            
            return temp_file.name
        except Exception as e:
            logger.error(f"Error trimming audio: {str(e)}")
            raise
            
    def adjust_volume(self, file_path: str, volume_db: float) -> str:
        """Adjust the volume of an audio file.
        
        Args:
            file_path (str): Path to the audio file
            volume_db (float): Volume adjustment in decibels
            
        Returns:
            str: Path to the adjusted audio file
        """
        try:
            # Load audio file
            audio = AudioSegment.from_file(file_path)
            
            # Adjust volume
            adjusted_audio = audio.apply_gain(volume_db)
            
            # Create temporary file for adjusted audio
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
            adjusted_audio.export(temp_file.name, format='mp3')
            
            return temp_file.name
        except Exception as e:
            logger.error(f"Error adjusting audio volume: {str(e)}")
            raise 