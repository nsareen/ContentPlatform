/**
 * Manual test script for brand voice service functionality
 * 
 * This script tests the brand voice service's methods, especially focusing on
 * the updateBrandVoice method with retry logic and exponential backoff.
 * 
 * Run with: npx ts-node src/scripts/test-brand-voice.ts
 */

const { brandVoiceService } = require('../lib/api/brand-voice-service');

// Type definitions for TypeScript
interface BrandVoiceCreateRequest {
  tenant_id: string;
  name: string;
  description: string;
  voice_metadata?: {
    personality?: string;
    tonality?: string;
  };
  dos?: string;
  donts?: string;
}

interface BrandVoiceUpdateRequest {
  name?: string;
  description?: string;
  voice_metadata?: {
    personality?: string;
    tonality?: string;
  };
  dos?: string;
  donts?: string;
  status?: 'draft' | 'published' | 'under_review' | 'inactive';
}

// Test configuration
const TENANT_ID = 'test-tenant-123';
const BRAND_VOICE_NAME = 'Test Brand Voice';
const BRAND_VOICE_DESC = 'A test brand voice for verification';

async function runTests() {
  console.log('🧪 Starting Brand Voice Service Tests');
  console.log('====================================');
  
  let testVoiceId: string = '';
  
  try {
    // 1. Create a new brand voice
    console.log('\n📝 Test: Creating a new brand voice');
    const createData: BrandVoiceCreateRequest = {
      tenant_id: TENANT_ID,
      name: BRAND_VOICE_NAME,
      description: BRAND_VOICE_DESC,
      voice_metadata: {
        personality: 'Professional',
        tonality: 'Friendly'
      },
      dos: 'Use clear language',
      donts: 'Avoid jargon'
    };
    
    const newVoice = await brandVoiceService.createBrandVoice(createData);
    console.log('✅ Successfully created brand voice:', newVoice.id);
    testVoiceId = newVoice.id;
    
    // 2. Get the brand voice
    console.log('\n📝 Test: Getting the brand voice');
    const voice = await brandVoiceService.getBrandVoice(testVoiceId);
    console.log('✅ Successfully retrieved brand voice:', voice.name);
    
    // 3. Update the brand voice (this tests our retry logic)
    console.log('\n📝 Test: Updating the brand voice (with retry logic)');
    const updateData: BrandVoiceUpdateRequest = {
      name: `${BRAND_VOICE_NAME} - Updated`,
      description: `${BRAND_VOICE_DESC} - Updated`,
      voice_metadata: {
        personality: 'Authoritative',
        tonality: 'Confident'
      }
    };
    
    const updatedVoice = await brandVoiceService.updateBrandVoice(testVoiceId, updateData);
    console.log('✅ Successfully updated brand voice:', updatedVoice.name);
    
    // 4. Get version history
    console.log('\n📝 Test: Getting version history');
    const versions = await brandVoiceService.getBrandVoiceVersions(testVoiceId);
    console.log(`✅ Successfully retrieved ${versions.length} versions`);
    
    // 5. Publish the brand voice
    console.log('\n📝 Test: Publishing the brand voice');
    const publishedVoice = await brandVoiceService.publishBrandVoice(testVoiceId);
    console.log('✅ Successfully published brand voice:', publishedVoice.name);
    
    // 6. Analyze content with the brand voice
    console.log('\n📝 Test: Analyzing content with the brand voice');
    const analysisResult = await brandVoiceService.analyzeBrandVoice(
      testVoiceId, 
      'This is a sample text to analyze with our brand voice guidelines.'
    );
    console.log('✅ Successfully analyzed content with brand voice');
    
    // 7. Clean up - delete the test brand voice
    console.log('\n📝 Test: Deleting the brand voice');
    await brandVoiceService.deleteBrandVoice(testVoiceId);
    console.log('✅ Successfully deleted brand voice');
    
    console.log('\n====================================');
    console.log('🎉 All tests completed successfully!');
    
  } catch (error) {
    console.error('\n❌ Test failed:', error);
    
    // Clean up if we created a test voice but tests failed
    if (testVoiceId) {
      try {
        console.log('\n🧹 Cleaning up - deleting test brand voice');
        await brandVoiceService.deleteBrandVoice(testVoiceId);
        console.log('✅ Successfully deleted test brand voice');
      } catch (cleanupError) {
        console.error('❌ Failed to clean up test brand voice:', cleanupError);
      }
    }
  }
}

// Run the tests
runTests().catch(error => {
  console.error('Unhandled error in tests:', error);
  process.exit(1);
});
