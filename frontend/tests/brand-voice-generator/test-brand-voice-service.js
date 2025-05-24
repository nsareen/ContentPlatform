/**
 * Test script for the Brand Voice Service API integration.
 * 
 * This script tests the frontend service that communicates with the backend API.
 * Run this script in a browser environment or using a test runner like Jest.
 */

import { brandVoiceService } from '../../src/lib/api/brand-voice-service';

// Sample content for testing
const SAMPLE_CONTENT = `
At Eco-Friendly Solutions, we believe that small changes can make a big impact. 
Our sustainable products are designed with the planet in mind, using only 
recyclable materials and ethical manufacturing processes. 
We're committed to reducing waste and helping our customers live more 
environmentally conscious lives. Join us in our mission to create a greener future!
`;

/**
 * Test the generateBrandVoice method of the brand voice service
 */
async function testGenerateBrandVoice() {
  console.log('Testing generateBrandVoice method...');
  
  try {
    const result = await brandVoiceService.generateBrandVoice({
      content: SAMPLE_CONTENT,
      brand_name: 'Eco-Friendly Solutions',
      industry: 'retail',
      options: {
        generation_depth: 'basic',
        include_sample_content: true
      }
    });
    
    // Validate the result
    if (!result.success) {
      throw new Error(`Generation failed: ${result.error || 'Unknown error'}`);
    }
    
    validateGeneratorResult(result);
    console.log('✅ generateBrandVoice test passed');
    return result;
  } catch (error) {
    console.error('❌ generateBrandVoice test failed:', error);
    throw error;
  }
}

/**
 * Test the saveBrandVoice method of the brand voice service
 */
async function testSaveBrandVoice(generatedResult) {
  console.log('Testing saveBrandVoice method...');
  
  try {
    const result = await brandVoiceService.saveBrandVoice({
      brand_voice_components: generatedResult.brand_voice_components,
      generation_metadata: generatedResult.generation_metadata,
      source_content: SAMPLE_CONTENT,
      name: 'Test Brand Voice',
      description: 'A test brand voice generated for frontend testing'
    });
    
    // Validate the result
    if (!result.success) {
      throw new Error(`Save failed: ${result.error || 'Unknown error'}`);
    }
    
    if (!result.brand_voice_id) {
      throw new Error('No brand_voice_id returned');
    }
    
    console.log('✅ saveBrandVoice test passed');
    return result;
  } catch (error) {
    console.error('❌ saveBrandVoice test failed:', error);
    throw error;
  }
}

/**
 * Validate the structure of the generator result
 */
function validateGeneratorResult(result) {
  // Check if the result is a valid object
  if (!result || typeof result !== 'object') {
    throw new Error('Result should be an object');
  }
  
  // Check if the result has the expected keys
  if (!result.success) {
    throw new Error('Result should have success=true');
  }
  
  // Check if brand_voice_components exists and has the expected structure
  if (!result.brand_voice_components) {
    throw new Error('Result should have brand_voice_components');
  }
  
  const components = result.brand_voice_components;
  
  // Validate components
  if (!Array.isArray(components.personality_traits) || components.personality_traits.length === 0) {
    throw new Error('personality_traits should be a non-empty array');
  }
  
  if (typeof components.tonality !== 'string' || components.tonality.length === 0) {
    throw new Error('tonality should be a non-empty string');
  }
  
  if (typeof components.identity !== 'string' || components.identity.length === 0) {
    throw new Error('identity should be a non-empty string');
  }
  
  if (!Array.isArray(components.dos) || components.dos.length === 0) {
    throw new Error('dos should be a non-empty array');
  }
  
  if (!Array.isArray(components.donts) || components.donts.length === 0) {
    throw new Error('donts should be a non-empty array');
  }
  
  // Check for sample content if it's included
  if (components.sample_content && (typeof components.sample_content !== 'string' || components.sample_content.length === 0)) {
    throw new Error('sample_content should be a non-empty string');
  }
  
  // Check if generation_metadata exists
  if (!result.generation_metadata) {
    throw new Error('Result should have generation_metadata');
  }
}

/**
 * Run all tests
 */
async function runAllTests() {
  console.log('Running Brand Voice Service Tests');
  console.log('--------------------------------');
  
  try {
    // Test the generate method
    const generatedResult = await testGenerateBrandVoice();
    
    // Test the save method using the result from the generate method
    const savedResult = await testSaveBrandVoice(generatedResult);
    
    console.log('\nAll brand voice service tests passed! ✅');
    console.log(`Generated brand voice ID: ${savedResult.brand_voice_id || 'N/A'}`);
    
    // Return the test results for further use
    return {
      generatedResult,
      savedResult
    };
  } catch (error) {
    console.error('\n❌ Tests failed:', error);
    throw error;
  }
}

// Execute the tests if this script is run directly
if (typeof window !== 'undefined' && window.runTests) {
  runAllTests()
    .then(results => {
      console.log('Test results:', results);
    })
    .catch(error => {
      console.error('Test execution failed:', error);
    });
}

export { runAllTests, testGenerateBrandVoice, testSaveBrandVoice };
