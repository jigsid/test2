from typing import List, Dict, Optional, Tuple
import logging
import os
import requests
from PIL import Image
import io
import tempfile
from dotenv import load_dotenv
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VisualGenerator:
    def __init__(self):
        """Initialize the visual generator with API configurations."""
        load_dotenv()
        self.api_key = os.getenv("HUGGINGFACE_API_KEY", "")  # Optional: for higher rate limits
        self.image_api_url = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"
        self.supported_styles = ['realistic', 'animated', 'abstract', 'cinematic']
        self.supported_sizes = [(1080, 1920), (720, 1280)]  # Portrait sizes
        
    def generate_scene_visuals(self, scene: Dict[str, any], 
                             style: str = 'realistic',
                             size: Tuple[int, int] = (1080, 1920)) -> str:
        """Generate visuals for a scene using Stable Diffusion.
        
        Args:
            scene (Dict): Scene description and parameters
            style (str): Visual style to apply
            size (Tuple[int, int]): Output image size
            
        Returns:
            str: Path to the generated image file
        """
        try:
            if style not in self.supported_styles:
                raise ValueError(f"Unsupported style. Supported styles: {self.supported_styles}")
                
            # Create image prompt
            prompt = self._create_image_prompt(scene, style)
            
            # Generate image
            image_data = self._generate_image(prompt)
            
            # Resize image to desired size
            image_data = image_data.resize(size, Image.Resampling.LANCZOS)
            
            # Save image to temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
            image_data.save(temp_file.name)
            
            return temp_file.name
        except Exception as e:
            logger.error(f"Error generating scene visuals: {str(e)}")
            raise
            
    def _create_image_prompt(self, scene: Dict[str, any], style: str) -> str:
        """Create a detailed prompt for image generation.
        
        Args:
            scene (Dict): Scene description and parameters
            style (str): Visual style to apply
            
        Returns:
            str: Formatted image generation prompt
        """
        base_prompt = scene['description']
        
        # Add style-specific keywords
        style_keywords = {
            'realistic': 'highly detailed, photorealistic, 8k uhd, high quality',
            'animated': '3D animation style, pixar style, vibrant colors, smooth textures',
            'abstract': 'abstract art, geometric shapes, modern art style, minimalist',
            'cinematic': 'cinematic lighting, movie scene, dramatic atmosphere, professional photography'
        }
        
        # Add composition guidelines for vertical video
        composition = "vertical composition, portrait orientation, centered composition"
        
        # Add quality boosters
        quality = "masterpiece, best quality, highly detailed"
        
        # Combine prompts
        full_prompt = f"{base_prompt}, {style_keywords[style]}, {composition}, {quality}"
        
        return full_prompt
        
    def _generate_image(self, prompt: str) -> Image.Image:
        """Generate image using Stable Diffusion through Hugging Face.
        
        Args:
            prompt (str): Image generation prompt
            
        Returns:
            Image.Image: Generated image
        """
        try:
            headers = {
                "Content-Type": "application/json"
            }
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            
            data = {
                "inputs": prompt,
                "parameters": {
                    "negative_prompt": "blurry, bad quality, distorted, deformed, ugly, bad anatomy",
                    "num_inference_steps": 50,
                    "guidance_scale": 7.5
                }
            }
            
            response = requests.post(self.image_api_url, headers=headers, json=data)
            response.raise_for_status()
            
            # Convert response to image
            image = Image.open(io.BytesIO(response.content))
            
            return image
        except Exception as e:
            logger.error(f"Error in image generation API call: {str(e)}")
            raise
            
    def apply_style_transfer(self, image_path: str, style: str) -> str:
        """Apply style transfer to an image.
        
        Args:
            image_path (str): Path to the input image
            style (str): Style to apply
            
        Returns:
            str: Path to the styled image
        """
        try:
            # Load image
            image = Image.open(image_path)
            
            # Apply style-specific processing
            if style == 'realistic':
                styled_image = self._apply_realistic_style(image)
            elif style == 'animated':
                styled_image = self._apply_animated_style(image)
            elif style == 'abstract':
                styled_image = self._apply_abstract_style(image)
            elif style == 'cinematic':
                styled_image = self._apply_cinematic_style(image)
            else:
                raise ValueError(f"Unsupported style: {style}")
                
            # Save styled image
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
            styled_image.save(temp_file.name)
            
            return temp_file.name
        except Exception as e:
            logger.error(f"Error applying style transfer: {str(e)}")
            raise
            
    def _apply_realistic_style(self, image: Image.Image) -> Image.Image:
        """Apply realistic style processing.
        
        Args:
            image (Image.Image): Input image
            
        Returns:
            Image.Image: Processed image
        """
        # Placeholder for realistic style processing
        # This would typically involve:
        # - Enhancing details
        # - Adjusting contrast and saturation
        # - Applying natural color grading
        return image
        
    def _apply_animated_style(self, image: Image.Image) -> Image.Image:
        """Apply animated style processing.
        
        Args:
            image (Image.Image): Input image
            
        Returns:
            Image.Image: Processed image
        """
        # Placeholder for animated style processing
        # This would typically involve:
        # - Simplifying colors
        # - Adding cel-shading effects
        # - Enhancing edges
        return image
        
    def _apply_abstract_style(self, image: Image.Image) -> Image.Image:
        """Apply abstract style processing.
        
        Args:
            image (Image.Image): Input image
            
        Returns:
            Image.Image: Processed image
        """
        # Placeholder for abstract style processing
        # This would typically involve:
        # - Geometric pattern overlay
        # - Color quantization
        # - Pattern generation
        return image
        
    def _apply_cinematic_style(self, image: Image.Image) -> Image.Image:
        """Apply cinematic style processing.
        
        Args:
            image (Image.Image): Input image
            
        Returns:
            Image.Image: Processed image
        """
        # Placeholder for cinematic style processing
        # This would typically involve:
        # - Color grading
        # - Vignette effect
        # - Film grain
        return image
        
    def create_text_overlay(self, image_path: str, text: str,
                          position: str = 'bottom') -> str:
        """Add text overlay to an image.
        
        Args:
            image_path (str): Path to the input image
            text (str): Text to overlay
            position (str): Position of the text
            
        Returns:
            str: Path to the image with text overlay
        """
        try:
            # Load image
            image = Image.open(image_path)
            
            # Create text overlay
            # This is a placeholder - actual implementation would:
            # 1. Choose appropriate font and size
            # 2. Calculate text position
            # 3. Add background/shadow for readability
            # 4. Render text on image
            
            # Save result
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
            image.save(temp_file.name)
            
            return temp_file.name
        except Exception as e:
            logger.error(f"Error creating text overlay: {str(e)}")
            raise 