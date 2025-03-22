"""
Style Profile Service

This module provides functionality for managing style profiles and generating
style embeddings for similarity search.
"""
import json
from typing import Dict, Any, List, Optional, Union

from openai import OpenAI
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.config import settings
from app.models.style_profile import StyleProfile
from app.schemas.style_profile import StyleProfileCreate, StyleProfileUpdate
from app.services.vision_service import vision_service


class StyleProfileService:
    """Service for managing style profiles and generating style embeddings"""
    
    def __init__(self):
        """Initialize the Style Profile Service with OpenAI client"""
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.embedding_model = settings.OPENAI_EMBEDDING_MODEL
        self.text_model = settings.OPENAI_TEXT_MODEL
    
    async def create_profile_from_analysis(
        self,
        db: Session,
        user_id: int,
        analysis_results: Dict[str, Any],
        profile_name: str = "Default Profile"
    ) -> StyleProfile:
        """
        Create a new style profile from image analysis results

        Args:
            db (Session): Database session
            user_id (int): User ID
            analysis_results (Dict[str, Any]): Results from image analysis
            profile_name (str): Name for the profile

        Returns:
            StyleProfile: Created style profile
        """
        # Extract relevant information from analysis results
        person_attributes = analysis_results.get("person_attributes", {})
        style_assessment = analysis_results.get("style_assessment", {})
        size_estimation = analysis_results.get("size_estimation", {})
        
        # Create style profile data
        profile_data = StyleProfileCreate(
            name=profile_name,
            body_shape=person_attributes.get("body_shape"),
            skin_tone=person_attributes.get("skin_tone"),
            height=None,  # Height would need conversion from estimation to cm
            sizes=size_estimation,
            style_preferences=style_assessment.get("style_descriptors", []),
            favorite_colors=style_assessment.get("color_palette", []),
            disliked_items=[]  # No info on disliked items from analysis
        )
        
        # Create the profile
        db_profile = StyleProfile(
            user_id=user_id,
            name=profile_data.name,
            description=profile_data.description,
            body_shape=profile_data.body_shape,
            skin_tone=profile_data.skin_tone,
            height=profile_data.height,
            sizes=profile_data.sizes,
            style_preferences=profile_data.style_preferences,
            favorite_colors=profile_data.favorite_colors,
            disliked_items=profile_data.disliked_items
        )
        
        # Generate style embedding
        style_embedding = await self.generate_style_embedding(db_profile)
        db_profile.style_embedding = style_embedding
        
        # Save to database
        db.add(db_profile)
        db.commit()
        db.refresh(db_profile)
        
        return db_profile
    
    async def update_profile_from_analysis(
        self,
        db: Session,
        profile_id: int,
        analysis_results: Dict[str, Any]
    ) -> StyleProfile:
        """
        Update an existing style profile from image analysis results

        Args:
            db (Session): Database session
            profile_id (int): Profile ID to update
            analysis_results (Dict[str, Any]): Results from image analysis

        Returns:
            StyleProfile: Updated style profile
        """
        # Get existing profile
        db_profile = db.query(StyleProfile).filter(StyleProfile.id == profile_id).first()
        if not db_profile:
            raise HTTPException(status_code=404, detail="Style profile not found")
        
        # Extract relevant information from analysis results
        person_attributes = analysis_results.get("person_attributes", {})
        style_assessment = analysis_results.get("style_assessment", {})
        size_estimation = analysis_results.get("size_estimation", {})
        
        # Update only non-None values
        if person_attributes.get("body_shape"):
            db_profile.body_shape = person_attributes.get("body_shape")
        
        if person_attributes.get("skin_tone"):
            db_profile.skin_tone = person_attributes.get("skin_tone")
        
        if size_estimation:
            # Merge existing sizes with new ones
            existing_sizes = db_profile.sizes or {}
            merged_sizes = {**existing_sizes, **size_estimation}
            db_profile.sizes = merged_sizes
        
        if style_assessment.get("style_descriptors"):
            # Merge with existing preferences, remove duplicates
            existing_prefs = db_profile.style_preferences or []
            new_prefs = style_assessment.get("style_descriptors", [])
            db_profile.style_preferences = list(set(existing_prefs + new_prefs))
        
        if style_assessment.get("color_palette"):
            # Merge with existing colors, remove duplicates
            existing_colors = db_profile.favorite_colors or []
            new_colors = style_assessment.get("color_palette", [])
            db_profile.favorite_colors = list(set(existing_colors + new_colors))
        
        # Generate updated style embedding
        style_embedding = await self.generate_style_embedding(db_profile)
        db_profile.style_embedding = style_embedding
        
        # Save to database
        db.commit()
        db.refresh(db_profile)
        
        return db_profile
    
    async def merge_profiles(
        self,
        db: Session,
        user_id: int,
        profile_ids: List[int],
        new_profile_name: str
    ) -> StyleProfile:
        """
        Merge multiple style profiles into a new one

        Args:
            db (Session): Database session
            user_id (int): User ID
            profile_ids (List[int]): List of profile IDs to merge
            new_profile_name (str): Name for the new profile

        Returns:
            StyleProfile: Merged profile
        """
        # Get profiles to merge
        profiles = db.query(StyleProfile).filter(
            StyleProfile.id.in_(profile_ids),
            StyleProfile.user_id == user_id
        ).all()
        
        if len(profiles) != len(profile_ids):
            raise HTTPException(status_code=404, detail="One or more profiles not found")
        
        # Initialize merged data
        merged_data = {
            "body_shape": None,
            "skin_tone": None,
            "height": None,
            "sizes": {},
            "style_preferences": [],
            "favorite_colors": [],
            "disliked_items": []
        }
        
        # Merge profile data
        for profile in profiles:
            # For single-value fields, take the most common value
            if profile.body_shape:
                merged_data["body_shape"] = profile.body_shape
            
            if profile.skin_tone:
                merged_data["skin_tone"] = profile.skin_tone
            
            if profile.height:
                merged_data["height"] = profile.height
            
            # Merge dictionaries and lists
            if profile.sizes:
                merged_data["sizes"].update(profile.sizes)
            
            if profile.style_preferences:
                merged_data["style_preferences"].extend(profile.style_preferences)
            
            if profile.favorite_colors:
                merged_data["favorite_colors"].extend(profile.favorite_colors)
            
            if profile.disliked_items:
                merged_data["disliked_items"].extend(profile.disliked_items)
        
        # Remove duplicates from lists
        merged_data["style_preferences"] = list(set(merged_data["style_preferences"]))
        merged_data["favorite_colors"] = list(set(merged_data["favorite_colors"]))
        merged_data["disliked_items"] = list(set(merged_data["disliked_items"]))
        
        # Create new profile
        db_profile = StyleProfile(
            user_id=user_id,
            name=new_profile_name,
            description=f"Merged profile from {len(profiles)} profiles",
            body_shape=merged_data["body_shape"],
            skin_tone=merged_data["skin_tone"],
            height=merged_data["height"],
            sizes=merged_data["sizes"],
            style_preferences=merged_data["style_preferences"],
            favorite_colors=merged_data["favorite_colors"],
            disliked_items=merged_data["disliked_items"]
        )
        
        # Generate style embedding
        style_embedding = await self.generate_style_embedding(db_profile)
        db_profile.style_embedding = style_embedding
        
        # Save to database
        db.add(db_profile)
        db.commit()
        db.refresh(db_profile)
        
        return db_profile
    
    async def generate_style_embedding(
        self,
        profile: Union[StyleProfile, Dict[str, Any]]
    ) -> List[float]:
        """
        Generate a vector embedding for a style profile

        Args:
            profile (Union[StyleProfile, Dict[str, Any]]): Style profile to embed

        Returns:
            List[float]: Embedding vector
        """
        # Convert profile to a text description for embedding
        if isinstance(profile, StyleProfile):
            profile_text = self._profile_to_text(profile)
        else:
            profile_text = self._profile_dict_to_text(profile)
        
        try:
            # Generate embedding
            response = self.client.embeddings.create(
                model=self.embedding_model,
                input=profile_text
            )
            
            return response.data[0].embedding
        
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error generating style embedding: {str(e)}"
            )
    
    async def find_similar_profiles(
        self,
        db: Session,
        embedding: List[float],
        limit: int = 5
    ) -> List[StyleProfile]:
        """
        Find profiles similar to the given embedding

        Args:
            db (Session): Database session
            embedding (List[float]): Embedding vector to compare against
            limit (int): Maximum number of results to return

        Returns:
            List[StyleProfile]: List of similar profiles
        """
        # This would typically use a vector database like Weaviate
        # For simplicity, we're implementing a basic version with SQLAlchemy
        
        # Get all profiles
        profiles = db.query(StyleProfile).all()
        
        # Calculate cosine similarity for each profile
        similarities = []
        for profile in profiles:
            if profile.style_embedding:
                similarity = self._cosine_similarity(embedding, profile.style_embedding)
                similarities.append((profile, similarity))
        
        # Sort by similarity (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Return top matches
        return [profile for profile, _ in similarities[:limit]]
    
    def _profile_to_text(self, profile: StyleProfile) -> str:
        """
        Convert a style profile to text description for embedding

        Args:
            profile (StyleProfile): Style profile to convert

        Returns:
            str: Text description
        """
        description = f"Body shape: {profile.body_shape or 'unknown'}. "
        description += f"Skin tone: {profile.skin_tone or 'unknown'}. "
        
        if profile.height:
            description += f"Height: {profile.height}cm. "
        
        if profile.sizes:
            sizes_str = ", ".join([f"{k}: {v}" for k, v in profile.sizes.items()])
            description += f"Sizes: {sizes_str}. "
        
        if profile.style_preferences:
            description += f"Style preferences: {', '.join(profile.style_preferences)}. "
        
        if profile.favorite_colors:
            description += f"Favorite colors: {', '.join(profile.favorite_colors)}. "
        
        if profile.disliked_items:
            description += f"Disliked items: {', '.join(profile.disliked_items)}."
        
        return description
    
    def _profile_dict_to_text(self, profile: Dict[str, Any]) -> str:
        """
        Convert a profile dictionary to text description for embedding

        Args:
            profile (Dict[str, Any]): Style profile dictionary to convert

        Returns:
            str: Text description
        """
        description = f"Body shape: {profile.get('body_shape') or 'unknown'}. "
        description += f"Skin tone: {profile.get('skin_tone') or 'unknown'}. "
        
        if profile.get('height'):
            description += f"Height: {profile.get('height')}cm. "
        
        if profile.get('sizes'):
            sizes_str = ", ".join([f"{k}: {v}" for k, v in profile.get('sizes', {}).items()])
            description += f"Sizes: {sizes_str}. "
        
        if profile.get('style_preferences'):
            description += f"Style preferences: {', '.join(profile.get('style_preferences', []))}. "
        
        if profile.get('favorite_colors'):
            description += f"Favorite colors: {', '.join(profile.get('favorite_colors', []))}. "
        
        if profile.get('disliked_items'):
            description += f"Disliked items: {', '.join(profile.get('disliked_items', []))}."
        
        return description
    
    @staticmethod
    def _cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        """
        Calculate cosine similarity between two vectors

        Args:
            vec1 (List[float]): First vector
            vec2 (List[float]): Second vector

        Returns:
            float: Cosine similarity (-1 to 1)
        """
        # Check if vectors have the same length
        if len(vec1) != len(vec2):
            raise ValueError("Vectors must have the same length")
        
        # Calculate dot product
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        
        # Calculate magnitudes
        magnitude1 = sum(a * a for a in vec1) ** 0.5
        magnitude2 = sum(b * b for b in vec2) ** 0.5
        
        # Calculate cosine similarity
        if magnitude1 == 0 or magnitude2 == 0:
            return 0
        
        return dot_product / (magnitude1 * magnitude2)


# Create a singleton instance
style_profile_service = StyleProfileService() 