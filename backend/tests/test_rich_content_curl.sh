#!/bin/bash

# Test the rich content generation API with curl
echo "Testing rich content generation API..."

# API endpoint
API_ENDPOINT="http://localhost:8000/api/rich-content/generate"

# Create a temporary JSON file for the request body
cat > request.json << EOL
{
  "prompt": "Create a marketing flyer for a new eco-friendly coffee shop called 'Green Bean' that emphasizes sustainable sourcing and biodegradable packaging.",
  "content_type": "flyer",
  "image_model": "dall-e-3",
  "image_quality": "standard",
  "image_size": "1024x1024",
  "image_style": "natural",
  "force_intent": "generate_rich_content"
}
EOL

# Make the request
echo "Sending request to $API_ENDPOINT..."
curl -X POST \
  -H "Content-Type: application/json" \
  -d @request.json \
  $API_ENDPOINT > response.json

# Check if the request was successful
if [ $? -eq 0 ]; then
  echo "Request successful! Response saved to response.json"
  
  # Display a summary of the response
  echo "Response summary:"
  echo "================="
  
  # Extract action and status
  ACTION=$(grep -o '"action":"[^"]*"' response.json | cut -d'"' -f4)
  STATUS=$(grep -o '"status":"[^"]*"' response.json | cut -d'"' -f4)
  
  echo "Action: $ACTION"
  echo "Status: $STATUS"
  
  # Count images
  IMAGE_COUNT=$(grep -o '"url"' response.json | wc -l)
  echo "Generated images: $IMAGE_COUNT"
  
  # Show the beginning of the text content
  TEXT_CONTENT=$(grep -o '"text_content":"[^"]*"' response.json | cut -d'"' -f4 | head -c 200)
  echo "Text content preview: $TEXT_CONTENT..."
else
  echo "Request failed!"
fi

# Clean up
rm request.json

echo "Test completed!"
