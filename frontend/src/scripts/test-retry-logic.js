/**
 * Test script to demonstrate the retry logic with exponential backoff
 * This is a simplified version of the updateBrandVoice method
 * that can be run directly with Node.js
 */

// Configuration
const MAX_RETRIES = 3;
const BACKOFF_FACTOR = 1.5;
const INITIAL_DELAY = 100; // 100ms for faster testing

// Mock API call that fails a certain number of times before succeeding
function mockApiCall(failCount) {
  let attempts = 0;
  
  return async function() {
    attempts++;
    console.log(`Attempt ${attempts}/${failCount + 1}`);
    
    if (attempts <= failCount) {
      throw new Error(`Simulated failure on attempt ${attempts}`);
    }
    
    return { success: true, data: { id: '123', name: 'Test Brand Voice' } };
  };
}

// Function with retry logic and exponential backoff
async function updateWithRetry(apiCall) {
  let retryCount = 0;
  let lastError = null;
  
  console.log('Starting update with retry logic and exponential backoff');
  console.log(`Configuration: MAX_RETRIES=${MAX_RETRIES}, BACKOFF_FACTOR=${BACKOFF_FACTOR}, INITIAL_DELAY=${INITIAL_DELAY}ms`);
  console.log('---------------------------------------------------');
  
  // Retry loop with exponential backoff
  while (retryCount <= MAX_RETRIES) {
    try {
      console.log(`Attempt ${retryCount + 1}/${MAX_RETRIES + 1}`);
      
      // Make the API call
      const result = await apiCall();
      
      console.log('✅ Success!', result);
      return result;
    } catch (error) {
      lastError = error;
      
      // If we've reached max retries, break out of the loop
      if (retryCount >= MAX_RETRIES) {
        console.log(`❌ Max retries (${MAX_RETRIES}) reached. Giving up.`);
        break;
      }
      
      // Log the retry attempt
      retryCount++;
      const delay = INITIAL_DELAY * Math.pow(BACKOFF_FACTOR, retryCount - 1);
      console.log(`❌ Attempt ${retryCount}/${MAX_RETRIES + 1} failed: ${error.message}`);
      console.log(`⏱️ Retrying in ${delay}ms...`);
      
      // Wait for the backoff delay before retrying
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }
  
  // All retries failed, enhance error information and throw
  console.error(`❌ All retries failed. Last error: ${lastError.message}`);
  
  // Create a more informative error object
  const enhancedError = new Error(
    `Failed after ${MAX_RETRIES} attempts. Please check your network connection and try again.`
  );
  
  // Add original error details if available
  enhancedError.originalError = lastError;
  enhancedError.originalMessage = lastError.message;
  
  throw enhancedError;
}

// Run test scenarios
async function runTests() {
  console.log('\n🧪 TEST 1: Success on first attempt');
  try {
    await updateWithRetry(mockApiCall(0));
    console.log('✅ Test 1 passed\n');
  } catch (error) {
    console.error('❌ Test 1 failed:', error.message, '\n');
  }
  
  console.log('\n🧪 TEST 2: Success after one retry');
  try {
    await updateWithRetry(mockApiCall(1));
    console.log('✅ Test 2 passed\n');
  } catch (error) {
    console.error('❌ Test 2 failed:', error.message, '\n');
  }
  
  console.log('\n🧪 TEST 3: Success on last allowed retry');
  try {
    await updateWithRetry(mockApiCall(MAX_RETRIES));
    console.log('✅ Test 3 passed\n');
  } catch (error) {
    console.error('❌ Test 3 failed:', error.message, '\n');
  }
  
  console.log('\n🧪 TEST 4: Failure after all retries');
  try {
    await updateWithRetry(mockApiCall(MAX_RETRIES + 1));
    console.error('❌ Test 4 failed: Expected an error but got success\n');
  } catch (error) {
    console.log('✅ Test 4 passed: Correctly failed after all retries\n');
    console.log('Error details:', error.message);
    if (error.originalError) {
      console.log('Original error:', error.originalMessage);
    }
  }
  
  console.log('\n🎉 All tests completed!');
}

// Run the tests
runTests().catch(error => {
  console.error('Unhandled error in tests:', error);
});
