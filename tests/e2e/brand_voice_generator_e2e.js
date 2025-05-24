/**
 * End-to-End Test for Brand Voice Generator
 * 
 * This script tests the entire brand voice generator workflow from the main application.
 * It uses Playwright to automate browser interactions.
 * 
 * Prerequisites:
 * - Backend server running on port 8001
 * - Frontend development server running
 * - Playwright installed: npm install -D playwright
 */

const { chromium } = require('playwright');

// Configuration
const APP_URL = 'http://localhost:3000'; // Adjust if your frontend runs on a different port
const TEST_TIMEOUT = 120000; // 2 minutes timeout for the entire test

// Sample content for testing
const SAMPLE_CONTENT = `
At Eco-Friendly Solutions, we believe that small changes can make a big impact. 
Our sustainable products are designed with the planet in mind, using only 
recyclable materials and ethical manufacturing processes. 
We're committed to reducing waste and helping our customers live more 
environmentally conscious lives. Join us in our mission to create a greener future!
`;

/**
 * Main test function
 */
async function runE2ETest() {
  console.log('Starting Brand Voice Generator E2E Test');
  console.log('--------------------------------------');
  
  const browser = await chromium.launch({
    headless: false, // Set to true for headless testing
    slowMo: 100 // Slow down operations by 100ms for better visibility
  });
  
  const context = await browser.newContext();
  const page = await context.newPage();
  
  try {
    // Step 1: Navigate to the application
    console.log('Step 1: Navigating to the application...');
    await page.goto(APP_URL);
    await page.waitForLoadState('networkidle');
    console.log('✅ Application loaded successfully');
    
    // Step 2: Navigate to the brand voices page
    console.log('Step 2: Navigating to brand voices page...');
    await page.click('text=Brand Voices');
    await page.waitForLoadState('networkidle');
    console.log('✅ Brand voices page loaded successfully');
    
    // Step 3: Open the floating actions menu
    console.log('Step 3: Opening the floating actions menu...');
    const floatingActionsButton = await page.locator('.fixed >> button >> nth=0');
    await floatingActionsButton.click();
    console.log('✅ Floating actions menu opened');
    
    // Step 4: Click on the brand voice generator button
    console.log('Step 4: Opening the brand voice generator...');
    await page.click('button[aria-label="Generate Voice"]');
    await page.waitForSelector('text=Brand Voice Generator');
    console.log('✅ Brand voice generator panel opened');
    
    // Step 5: Fill the generator form
    console.log('Step 5: Filling the generator form...');
    await page.fill('input[placeholder*="Maybelline"]', 'Eco-Friendly Solutions');
    await page.selectOption('select', { label: 'Retail' });
    await page.fill('textarea', SAMPLE_CONTENT);
    console.log('✅ Generator form filled');
    
    // Step 6: Generate the brand voice
    console.log('Step 6: Generating the brand voice...');
    await page.click('text=Generate Brand Voice');
    
    // Wait for the generation to complete (this might take some time)
    await page.waitForSelector('text=Generated Brand Voice', { timeout: 60000 });
    console.log('✅ Brand voice generated successfully');
    
    // Step 7: Open the full generator interface
    console.log('Step 7: Opening the full generator interface...');
    await page.click('text=Open Full Generator to Save');
    await page.waitForSelector('text=AI Brand Voice Generator');
    console.log('✅ Full generator interface opened');
    
    // Step 8: Save the brand voice
    console.log('Step 8: Saving the brand voice...');
    await page.fill('input[placeholder*="Enter a name"]', 'E2E Test Brand Voice');
    await page.fill('textarea[placeholder*="Add a description"]', 'Brand voice created during E2E testing');
    await page.click('text=Save Brand Voice');
    
    // Wait for the save to complete
    await page.waitForSelector('text=Brand Voice Saved Successfully', { timeout: 30000 });
    console.log('✅ Brand voice saved successfully');
    
    // Step 9: Navigate to the brand voices list
    console.log('Step 9: Navigating to brand voices list...');
    await page.click('text=Go to Brand Voices');
    await page.waitForSelector('text=E2E Test Brand Voice');
    console.log('✅ Brand voice appears in the list');
    
    // Step 10: Open the brand voice details
    console.log('Step 10: Opening brand voice details...');
    await page.click('text=E2E Test Brand Voice');
    await page.waitForSelector('text=Personality Traits');
    console.log('✅ Brand voice details loaded successfully');
    
    // Step 11: Verify that the analyzer is available
    console.log('Step 11: Checking for analyzer functionality...');
    const analyzerButton = await page.locator('button[aria-label="Analyzer"]');
    await analyzerButton.click();
    await page.waitForSelector('text=Analyze Content');
    console.log('✅ Analyzer functionality is available');
    
    console.log('\nAll E2E tests passed! ✅');
  } catch (error) {
    console.error('\n❌ E2E test failed:', error);
    
    // Take a screenshot of the failure
    await page.screenshot({ path: 'e2e-test-failure.png' });
    console.log('Screenshot of failure saved as e2e-test-failure.png');
    
    throw error;
  } finally {
    // Clean up
    await browser.close();
  }
}

// Run the test if executed directly
if (require.main === module) {
  runE2ETest()
    .then(() => process.exit(0))
    .catch(() => process.exit(1));
}

module.exports = { runE2ETest };
