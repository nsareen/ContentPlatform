"""
Proxy API for handling CORS issues with third-party image URLs
"""

import httpx
from fastapi import APIRouter, Depends, HTTPException, Response, Query
from fastapi.responses import StreamingResponse
from typing import Optional, List
import io
import logging
import traceback
import urllib.parse
from starlette.responses import JSONResponse

from app.core.auth import get_current_active_user
from app.models.models import User

router = APIRouter(
    prefix="/proxy",
    tags=["proxy"],
)

# Configure detailed logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

@router.get("/image")
async def proxy_image(
    url: str = Query(..., description="The URL of the image to proxy")
    # Removed authentication for testing
    # current_user: User = Depends(get_current_active_user)
):
    """
    Proxy an image from a third-party URL to avoid CORS issues.
    
    This endpoint fetches an image from the provided URL and returns it with appropriate
    CORS headers to allow it to be displayed in the frontend.
    """
    try:
        logger.info(f"Proxying image from URL: {url}")
        
        # Parse the URL to extract domain
        parsed_url = urllib.parse.urlparse(url)
        domain = parsed_url.netloc
        logger.debug(f"Parsed URL domain: {domain}")
        
        # In development, allow all domains for testing
        # In production, you would restrict to only trusted domains
        allowed_domains = [
            # OpenAI DALL-E domains
            "oaidalleapiprodscus.blob.core.windows.net",
            "openai-labs-public-images-prod.azureedge.net",
            "dalleprodsec.blob.core.windows.net",
            # Public image services for testing
            "images.unsplash.com",
            "picsum.photos",
            "fastly.picsum.photos",
            "placehold.co",
            "via.placeholder.com",
            # Allow any domain for testing
            # Remove this in production
            "*"
        ]
        
        # For development, we're allowing all domains
        # In production, uncomment this check
        # if not any(domain == allowed_domain or allowed_domain == "*" for allowed_domain in allowed_domains):
        #     logger.warning(f"Attempted to proxy image from non-allowed domain: {domain}")
        #     return JSONResponse(
        #         status_code=403, 
        #         content={"error": "URL domain not allowed for proxying", "domain": domain}
        #     )
            
        # Log the full URL and components for debugging
        logger.debug(f"Full URL being proxied: {url}")
        logger.debug(f"URL components: scheme={parsed_url.scheme}, netloc={parsed_url.netloc}, path={parsed_url.path}")
        logger.debug(f"URL query params: {parsed_url.query}")
        
        # Configure client with appropriate headers and timeout
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Cache-Control": "no-cache",
            "Pragma": "no-cache",
        }
        
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            try:
                # Use a longer timeout for OpenAI URLs which might be slow to respond
                logger.debug(f"Sending request to URL: {url}")
                response = await client.get(url, headers=headers)
                
                logger.debug(f"Response status code: {response.status_code}")
                logger.debug(f"Response headers: {dict(response.headers)}")
                
                if response.status_code != 200:
                    error_msg = f"Failed to fetch image from URL: {url}, status code: {response.status_code}"
                    logger.error(error_msg)
                    return JSONResponse(
                        status_code=response.status_code, 
                        content={"error": error_msg, "status_code": response.status_code}
                    )
                    
                # Log content length for debugging
                content_length = len(response.content)
                logger.debug(f"Successfully fetched image, content length: {content_length} bytes")
                
                if content_length == 0:
                    error_msg = "Received empty response from URL"
                    logger.error(error_msg)
                    return JSONResponse(
                        status_code=500, 
                        content={"error": error_msg}
                    )
                
                # Check if the content type is an image
                content_type = response.headers.get("content-type", "")
                logger.debug(f"Content-Type: {content_type}")
                
                if not content_type.startswith("image/") and "application/octet-stream" not in content_type:
                    logger.warning(f"Response is not an image. Content-Type: {content_type}")
                    # Continue anyway, but log the warning
            except httpx.TimeoutException as e:
                error_msg = f"Timeout fetching image from URL: {url}"
                logger.error(error_msg)
                logger.error(traceback.format_exc())
                return JSONResponse(
                    status_code=504, 
                    content={"error": error_msg, "exception": str(e)}
                )
            except httpx.RequestError as e:
                error_msg = f"Request error fetching image: {str(e)}"
                logger.error(error_msg)
                logger.error(traceback.format_exc())
                return JSONResponse(
                    status_code=502, 
                    content={"error": error_msg, "exception": str(e)}
                )
            except Exception as e:
                error_msg = f"Unexpected error: {str(e)}"
                logger.error(error_msg)
                logger.error(traceback.format_exc())
                return JSONResponse(
                    status_code=500, 
                    content={"error": error_msg, "exception": str(e)}
                )
            
            # Get content type from response headers or default to image/jpeg
            content_type = response.headers.get("content-type", "image/jpeg")
            if not content_type or content_type == "application/octet-stream":
                # Try to guess content type from URL or default to image/jpeg
                if url.lower().endswith(".png"):
                    content_type = "image/png"
                elif url.lower().endswith(".jpg") or url.lower().endswith(".jpeg"):
                    content_type = "image/jpeg"
                elif url.lower().endswith(".gif"):
                    content_type = "image/gif"
                elif url.lower().endswith(".webp"):
                    content_type = "image/webp"
                else:
                    content_type = "image/jpeg"  # Default
            
            logger.debug(f"Using content type: {content_type}")
            
            # Return the image with appropriate headers
            return StreamingResponse(
                io.BytesIO(response.content),
                media_type=content_type,
                headers={
                    "Access-Control-Allow-Origin": "*",
                    "Cache-Control": "public, max-age=3600",
                    "Content-Disposition": "inline",
                    "X-Content-Type-Options": "nosniff",
                    "X-Frame-Options": "SAMEORIGIN",
                    "Content-Security-Policy": "default-src 'self'; img-src 'self' data: *"
                }
            )
    except Exception as e:
        error_msg = f"Error proxying image: {str(e)}"
        logger.exception(error_msg)
        logger.error(traceback.format_exc())
        return JSONResponse(
            status_code=500, 
            content={"error": error_msg, "exception": str(e)}
        )
