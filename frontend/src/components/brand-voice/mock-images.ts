// Mock image URLs for testing when the backend can't generate real images
export const mockImages = [
  {
    url: 'https://placehold.co/800x600/6D3BEB/FFFFFF?text=Marketing+Image+1',
    description: 'A marketing image for promotional materials'
  },
  {
    url: 'https://placehold.co/800x600/3B82F6/FFFFFF?text=Product+Image',
    description: 'A product image showcasing features and benefits'
  },
  {
    url: 'https://placehold.co/800x600/10B981/FFFFFF?text=Lifestyle+Image',
    description: 'A lifestyle image showing the product in use'
  },
  {
    url: 'https://placehold.co/800x600/F59E0B/FFFFFF?text=Brand+Image',
    description: 'A brand image representing company values'
  }
];

// Function to get a random mock image
export function getRandomMockImage() {
  const randomIndex = Math.floor(Math.random() * mockImages.length);
  return mockImages[randomIndex];
}

// Function to get multiple random mock images
export function getRandomMockImages(count: number) {
  const result = [];
  const availableImages = [...mockImages];
  
  // If we need more images than available, we'll reuse some
  for (let i = 0; i < count; i++) {
    if (availableImages.length === 0) {
      // If we've used all available images, reset the array
      availableImages.push(...mockImages);
    }
    
    // Get a random index from the available images
    const randomIndex = Math.floor(Math.random() * availableImages.length);
    
    // Add the image to the result and remove it from available images
    result.push(availableImages[randomIndex]);
    availableImages.splice(randomIndex, 1);
  }
  
  return result;
}
