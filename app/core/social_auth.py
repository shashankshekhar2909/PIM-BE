import requests
from typing import Optional, Dict, Any
from fastapi import HTTPException
import logging

class SocialAuthService:
    """Service to handle social authentication with OAuth providers."""
    
    @staticmethod
    def get_google_user_info(access_token: str) -> Optional[Dict[str, Any]]:
        """Get user information from Google using access token."""
        try:
            response = requests.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logging.error(f"Failed to get Google user info: {str(e)}")
            return None
    
    @staticmethod
    def get_github_user_info(access_token: str) -> Optional[Dict[str, Any]]:
        """Get user information from GitHub using access token."""
        try:
            response = requests.get(
                "https://api.github.com/user",
                headers={
                    "Authorization": f"token {access_token}",
                    "Accept": "application/vnd.github.v3+json"
                }
            )
            response.raise_for_status()
            user_data = response.json()
            
            # Get email from GitHub
            email_response = requests.get(
                "https://api.github.com/user/emails",
                headers={
                    "Authorization": f"token {access_token}",
                    "Accept": "application/vnd.github.v3+json"
                }
            )
            email_response.raise_for_status()
            emails = email_response.json()
            
            # Find primary email
            primary_email = None
            for email in emails:
                if email.get("primary") and email.get("verified"):
                    primary_email = email.get("email")
                    break
            
            if not primary_email:
                raise HTTPException(status_code=400, detail="No verified email found for GitHub account")
            
            return {
                "id": user_data.get("id"),
                "email": primary_email,
                "name": user_data.get("name"),
                "avatar_url": user_data.get("avatar_url")
            }
        except Exception as e:
            logging.error(f"Failed to get GitHub user info: {str(e)}")
            return None
    
    @staticmethod
    def get_facebook_user_info(access_token: str) -> Optional[Dict[str, Any]]:
        """Get user information from Facebook using access token."""
        try:
            response = requests.get(
                f"https://graph.facebook.com/me?fields=id,name,email&access_token={access_token}"
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logging.error(f"Failed to get Facebook user info: {str(e)}")
            return None
    
    @staticmethod
    def get_user_info(provider: str, access_token: str) -> Optional[Dict[str, Any]]:
        """Get user information from the specified OAuth provider."""
        if provider == "google":
            return SocialAuthService.get_google_user_info(access_token)
        elif provider == "github":
            return SocialAuthService.get_github_user_info(access_token)
        elif provider == "facebook":
            return SocialAuthService.get_facebook_user_info(access_token)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported provider: {provider}") 