/**
 * Integration tests for the Content Platform
 * Tests the communication between frontend and backend
 */

const { chromium } = require('playwright');
const assert = require('assert');

// Configuration
const FRONTEND_URL = 'http://localhost:3000';
const BACKEND_URL = 'http://localhost:8000';
const TEST_TIMEOUT = 30000; // 30 seconds

// Test suite
describe('Content Platform Integration Tests', () => {
  let browser;
  let page;

  // Setup
  before(async () => {
    // Launch browser
    browser = await chromium.launch({
      headless: true, // Set to false for debugging
    });
  });

  // Teardown
  after(async () => {
    // Close browser
    if (browser) {
      await browser.close();
    }
  });

  // Before each test
  beforeEach(async () => {
    // Create new page
    page = await browser.newPage();
    
    // Set timeout
    page.setDefaultTimeout(TEST_TIMEOUT);
    
    // Enable console logging
    page.on('console', msg => console.log(`[Browser Console] ${msg.type()}: ${msg.text()}`));
  });

  // After each test
  afterEach(async () => {
    // Close page
    if (page) {
      await page.close();
    }
  });

  // Test authentication
  it('should authenticate with development token', async () => {
    // Navigate to home page
    await page.goto(FRONTEND_URL);
    
    // Wait for authentication to complete
    await page.waitForTimeout(2000);
    
    // Check local storage for auth token
    const token = await page.evaluate(() => localStorage.getItem('auth_token'));
    
    // Assert token exists
    assert.ok(token, 'Authentication token should exist in localStorage');
    assert.ok(token.length > 0, 'Authentication token should not be empty');
  });

  // Test brand voices page
  it('should load brand voices page', async () => {
    // Navigate to brand voices page
    await page.goto(`${FRONTEND_URL}/brand-voices`);
    
    // Wait for page to load
    await page.waitForSelector('h1:has-text("Brand Voices")');
    
    // Check if brand voices are loaded
    const brandVoicesCount = await page.evaluate(() => {
      // Look for brand voice cards or list items
      const cards = document.querySelectorAll('[data-testid="brand-voice-card"]');
      if (cards.length > 0) return cards.length;
      
      // If no cards found, check for any content that indicates brand voices
      const content = document.querySelector('main').textContent;
      return content.includes('No brand voices found') ? 0 : -1;
    });
    
    // Assert brand voices are loaded or empty state is shown
    assert.ok(brandVoicesCount >= 0, 'Brand voices page should load successfully');
  });

  // Test creating a brand voice
  it('should create a new brand voice', async () => {
    // Navigate to brand voices page
    await page.goto(`${FRONTEND_URL}/brand-voices`);
    
    // Wait for page to load
    await page.waitForSelector('h1:has-text("Brand Voices")');
    
    // Click on "Create Brand Voice" button
    await page.click('text="Create Brand Voice"');
    
    // Wait for create page to load
    await page.waitForSelector('form');
    
    // Fill out form
    await page.fill('input[name="name"]', 'Integration Test Brand Voice');
    await page.fill('textarea[name="description"]', 'Created by integration test');
    
    // Fill personality and tonality if they exist
    const hasPersonality = await page.$('input[name="personality"]');
    if (hasPersonality) {
      await page.fill('input[name="personality"]', 'Bold, Innovative');
    }
    
    const hasTonality = await page.$('input[name="tonality"]');
    if (hasTonality) {
      await page.fill('input[name="tonality"]', 'Confident, Professional');
    }
    
    // Fill dos and donts
    await page.fill('textarea[name="dos"]', 'Do use clear language\nDo be concise');
    await page.fill('textarea[name="donts"]', 'Don\'t use jargon\nDon\'t be verbose');
    
    // Submit form
    await page.click('button[type="submit"]');
    
    // Wait for redirect to brand voices page
    await page.waitForSelector('h1:has-text("Brand Voices")');
    
    // Check if new brand voice is in the list
    const newBrandVoiceExists = await page.evaluate(() => {
      return document.body.textContent.includes('Integration Test Brand Voice');
    });
    
    // Assert new brand voice exists
    assert.ok(newBrandVoiceExists, 'Newly created brand voice should appear in the list');
  });

  // Test editing a brand voice
  it('should edit an existing brand voice', async () => {
    // Navigate to brand voices page
    await page.goto(`${FRONTEND_URL}/brand-voices`);
    
    // Wait for page to load
    await page.waitForSelector('h1:has-text("Brand Voices")');
    
    // Find the Integration Test Brand Voice
    const editButtonSelector = 'text="Integration Test Brand Voice" >> xpath=ancestor::div[contains(@class, "border")]//button[contains(text(), "Edit")]';
    
    // Click edit button
    await page.click(editButtonSelector);
    
    // Wait for edit page to load
    await page.waitForSelector('form');
    
    // Update description
    await page.fill('textarea[name="description"]', 'Updated by integration test');
    
    // Submit form
    await page.click('button[type="submit"]');
    
    // Wait for redirect to brand voices page
    await page.waitForSelector('h1:has-text("Brand Voices")');
    
    // Check if brand voice description is updated
    const updatedDescriptionExists = await page.evaluate(() => {
      return document.body.textContent.includes('Updated by integration test');
    });
    
    // Assert description is updated
    assert.ok(updatedDescriptionExists, 'Brand voice description should be updated');
  });

  // Test publishing a brand voice
  it('should publish a brand voice', async () => {
    // Navigate to brand voices page
    await page.goto(`${FRONTEND_URL}/brand-voices`);
    
    // Wait for page to load
    await page.waitForSelector('h1:has-text("Brand Voices")');
    
    // Find the Integration Test Brand Voice
    const publishButtonSelector = 'text="Integration Test Brand Voice" >> xpath=ancestor::div[contains(@class, "border")]//button[contains(text(), "Publish")]';
    
    // Check if publish button exists (might already be published)
    const publishButtonExists = await page.$(publishButtonSelector);
    
    if (publishButtonExists) {
      // Click publish button
      await page.click(publishButtonSelector);
      
      // Wait for confirmation dialog if it exists
      const confirmButtonExists = await page.$('text="Confirm"');
      if (confirmButtonExists) {
        await page.click('text="Confirm"');
      }
      
      // Wait for page to update
      await page.waitForTimeout(1000);
    }
    
    // Check if brand voice is published
    const isPublished = await page.evaluate(() => {
      return document.body.textContent.includes('Integration Test Brand Voice') && 
             document.body.textContent.includes('Published');
    });
    
    // Assert brand voice is published
    assert.ok(isPublished, 'Brand voice should be published');
  });

  // Test deleting a brand voice
  it('should delete a brand voice', async () => {
    // Navigate to brand voices page
    await page.goto(`${FRONTEND_URL}/brand-voices`);
    
    // Wait for page to load
    await page.waitForSelector('h1:has-text("Brand Voices")');
    
    // Find the Integration Test Brand Voice
    const deleteButtonSelector = 'text="Integration Test Brand Voice" >> xpath=ancestor::div[contains(@class, "border")]//button[contains(text(), "Delete")]';
    
    // Click delete button
    await page.click(deleteButtonSelector);
    
    // Wait for confirmation dialog
    await page.waitForSelector('text="Are you sure"');
    
    // Confirm deletion
    await page.click('text="Delete"');
    
    // Wait for page to update
    await page.waitForTimeout(1000);
    
    // Check if brand voice is deleted
    const brandVoiceDeleted = await page.evaluate(() => {
      return !document.body.textContent.includes('Integration Test Brand Voice');
    });
    
    // Assert brand voice is deleted
    assert.ok(brandVoiceDeleted, 'Brand voice should be deleted');
  });
});
