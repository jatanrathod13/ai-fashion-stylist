"""
Vision Service

This module provides image analysis capabilities using OpenAI's GPT-4o Vision API.
"""
import os
import json
import base64
from typing import Dict, Any, List, Optional

from openai import OpenAI
from fastapi import UploadFile, HTTPException
from PIL import Image as PILImage

from app.config import settings


class VisionService:
    """Service for analyzing images using OpenAI's GPT-4o Vision API"""
    
    def __init__(self):
        """Initialize the Vision Service with OpenAI client"""
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_VISION_MODEL
    
    async def analyze_image(
        self, 
        image_path: str, 
        analysis_type: str = "full"
    ) -> Dict[str, Any]:
        """
        Analyze an image using GPT-4o Vision

        Args:
            image_path (str): Path to the image file
            analysis_type (str): Type of analysis to perform (full, clothing, body, etc.)

        Returns:
            Dict[str, Any]: Analysis results
        """
        try:
            # Read and encode the image
            with open(image_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode("utf-8")
            
            # Select the appropriate prompt based on analysis type
            prompt = self._get_analysis_prompt(analysis_type)
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": prompt
                    },
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Please analyze this image."},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                response_format={"type": "json_object"}
            )
            
            # Parse the response
            analysis_results = json.loads(response.choices[0].message.content)
            
            return analysis_results
        
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error analyzing image: {str(e)}"
            )
    
    async def extract_clothing_items(self, image_path: str) -> List[Dict[str, Any]]:
        """
        Extract clothing items from an image

        Args:
            image_path (str): Path to the image file

        Returns:
            List[Dict[str, Any]]: List of detected clothing items
        """
        analysis_results = await self.analyze_image(image_path, "clothing")
        return analysis_results.get("clothing_items", [])
    
    async def analyze_body_attributes(self, image_path: str) -> Dict[str, Any]:
        """
        Analyze body attributes from an image

        Args:
            image_path (str): Path to the image file

        Returns:
            Dict[str, Any]: Detected body attributes
        """
        analysis_results = await self.analyze_image(image_path, "body")
        return analysis_results.get("body_attributes", {})
    
    def _get_analysis_prompt(self, analysis_type: str) -> str:
        """
        Get the appropriate prompt for the analysis type

        Args:
            analysis_type (str): Type of analysis to perform

        Returns:
            str: Analysis prompt for the model
        """
        prompts = {
            "full": """You are an expert fashion analyst. Analyze the provided image and extract the following information:
                1. Person attributes: body shape, skin tone, height estimation
                2. Clothing items: identify all visible clothing items, their colors, patterns, and styles
                3. Style assessment: evaluate the overall style, identify dominant fashion categories
                4. Size estimation: estimate clothing sizes based on the image
                
                Provide all information in a structured JSON format with the following schema:
                {
                    "person_attributes": {
                        "body_shape": string,  // e.g., "hourglass", "rectangle", "pear", "inverted triangle", "apple"
                        "skin_tone": string,  // e.g., "warm", "cool", "neutral"
                        "height_estimation": string  // e.g., "tall", "average", "short"
                    },
                    "clothing_items": [
                        {
                            "item_type": string,  // e.g., "top", "bottom", "dress", "shoes", "accessory"
                            "description": string,
                            "color": string,
                            "pattern": string,  // e.g., "solid", "striped", "floral"
                            "material": string,  // e.g., "cotton", "denim", "leather"
                            "style": string,  // e.g., "casual", "formal", "bohemian"
                            "fit": string  // e.g., "loose", "fitted", "oversized"
                        }
                    ],
                    "style_assessment": {
                        "overall_style": string,  // e.g., "casual", "bohemian", "minimalist"
                        "style_descriptors": [string],
                        "color_palette": [string]
                    },
                    "size_estimation": {
                        "tops": string,  // e.g., "S", "M", "L"
                        "bottoms": string,  // e.g., "30", "32", "34"
                        "shoes": string  // e.g., "8", "9", "10"
                    }
                }
                """,
            
            "clothing": """You are an expert fashion analyst. Analyze the provided image and identify all visible clothing items.
                For each item, extract the following details:
                - Item type (top, bottom, dress, etc.)
                - Description
                - Color
                - Pattern
                - Material (if discernible)
                - Style categorization
                
                Provide all information in a structured JSON format with the following schema:
                {
                    "clothing_items": [
                        {
                            "item_type": string,
                            "description": string,
                            "color": string,
                            "pattern": string,
                            "material": string,
                            "style": string
                        }
                    ]
                }
                """,
            
            "body": """You are an expert fashion analyst. Analyze the provided image and extract physical attributes 
                relevant to fashion recommendations.
                
                Extract the following details:
                - Body shape (hourglass, rectangle, pear, inverted triangle, apple)
                - Skin tone (warm, cool, neutral)
                - Height estimation
                - Size estimations for clothing categories
                
                Provide all information in a structured JSON format with the following schema:
                {
                    "body_attributes": {
                        "body_shape": string,
                        "skin_tone": string,
                        "height_estimation": string,
                        "size_estimation": {
                            "tops": string,
                            "bottoms": string,
                            "shoes": string
                        }
                    }
                }
                """
        }
        
        return prompts.get(analysis_type, prompts["full"])
    
    @staticmethod
    async def get_image_dimensions(image_path: str) -> Dict[str, int]:
        """
        Get the dimensions of an image

        Args:
            image_path (str): Path to the image file

        Returns:
            Dict[str, int]: Dictionary with width and height
        """
        try:
            with PILImage.open(image_path) as img:
                width, height = img.size
                return {"width": width, "height": height}
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error getting image dimensions: {str(e)}"
            )


# Create a singleton instance
vision_service = VisionService() 