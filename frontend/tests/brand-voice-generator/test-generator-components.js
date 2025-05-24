/**
 * Test script for the Brand Voice Generator UI components.
 * 
 * This script tests the React components for the brand voice generator.
 * It requires a testing library like React Testing Library or Enzyme.
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { BrandVoicePreview } from '../../src/components/brand-voice/generator-components';
import { FloatingGeneratorPanel } from '../../src/components/brand-voice/generator-components';
import GeneratorPanel from '../../src/components/brand-voice/generator-panel';
import { brandVoiceService } from '../../src/lib/api/brand-voice-service';

// Mock the brand voice service
jest.mock('../../src/lib/api/brand-voice-service', () => ({
  brandVoiceService: {
    generateBrandVoice: jest.fn(),
    saveBrandVoice: jest.fn()
  }
}));

// Sample brand voice data for testing
const sampleBrandVoice = {
  personality_traits: ['Eco-conscious', 'Innovative', 'Responsible', 'Optimistic', 'Educational'],
  tonality: 'Friendly, informative, and passionate about sustainability. Uses positive language to inspire action.',
  identity: 'A forward-thinking brand dedicated to environmental sustainability, offering practical solutions for eco-conscious consumers.',
  dos: [
    'Emphasize environmental benefits',
    'Use positive, action-oriented language',
    'Include facts about sustainability',
    'Maintain an optimistic tone about environmental impact',
    'Educate customers about sustainable practices'
  ],
  donts: [
    'Use alarmist language about climate issues',
    'Make exaggerated claims about product benefits',
    'Use overly technical jargon',
    'Sound judgmental of non-eco-friendly choices',
    'Focus solely on problems without offering solutions'
  ],
  sample_content: 'Introducing our new bamboo kitchen set - designed with sustainability in mind. These durable, plastic-free alternatives help reduce your environmental footprint while adding natural beauty to your home. Each purchase supports our tree-planting initiative.'
};

// Sample content for testing
const SAMPLE_CONTENT = `
At Eco-Friendly Solutions, we believe that small changes can make a big impact. 
Our sustainable products are designed with the planet in mind, using only 
recyclable materials and ethical manufacturing processes. 
We're committed to reducing waste and helping our customers live more 
environmentally conscious lives. Join us in our mission to create a greener future!
`;

/**
 * Test the BrandVoicePreview component
 */
describe('BrandVoicePreview Component', () => {
  test('renders brand voice data correctly', () => {
    render(<BrandVoicePreview brandVoice={sampleBrandVoice} />);
    
    // Check if personality traits are rendered
    sampleBrandVoice.personality_traits.forEach(trait => {
      expect(screen.getByText(trait)).toBeInTheDocument();
    });
    
    // Check if tonality is rendered
    expect(screen.getByText(sampleBrandVoice.tonality)).toBeInTheDocument();
    
    // Check if identity is rendered
    expect(screen.getByText(sampleBrandVoice.identity)).toBeInTheDocument();
    
    // Check if dos are rendered
    sampleBrandVoice.dos.forEach(item => {
      expect(screen.getByText(item)).toBeInTheDocument();
    });
    
    // Check if donts are rendered
    sampleBrandVoice.donts.forEach(item => {
      expect(screen.getByText(item)).toBeInTheDocument();
    });
    
    // Check if sample content is rendered
    expect(screen.getByText(sampleBrandVoice.sample_content)).toBeInTheDocument();
  });
  
  test('edit buttons trigger callbacks when clicked', () => {
    const onEditMock = jest.fn();
    render(<BrandVoicePreview brandVoice={sampleBrandVoice} onEdit={onEditMock} />);
    
    // Find all edit buttons
    const editButtons = screen.getAllByText('Edit');
    
    // Click each edit button and check if the callback is called with the correct section
    fireEvent.click(editButtons[0]); // Personality traits
    expect(onEditMock).toHaveBeenCalledWith('personality_traits');
    
    fireEvent.click(editButtons[1]); // Identity
    expect(onEditMock).toHaveBeenCalledWith('identity');
    
    fireEvent.click(editButtons[2]); // Dos
    expect(onEditMock).toHaveBeenCalledWith('dos');
    
    fireEvent.click(editButtons[3]); // Donts
    expect(onEditMock).toHaveBeenCalledWith('donts');
    
    fireEvent.click(editButtons[4]); // Sample content
    expect(onEditMock).toHaveBeenCalledWith('sample_content');
  });
});

/**
 * Test the FloatingGeneratorPanel component
 */
describe('FloatingGeneratorPanel Component', () => {
  beforeEach(() => {
    // Reset mocks
    jest.clearAllMocks();
  });
  
  test('renders input form correctly', () => {
    const onCloseMock = jest.fn();
    render(<FloatingGeneratorPanel onClose={onCloseMock} />);
    
    // Check if form elements are rendered
    expect(screen.getByPlaceholderText(/e.g., Maybelline Singapore/i)).toBeInTheDocument();
    expect(screen.getByText('Select Industry')).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/Paste sample content/i)).toBeInTheDocument();
    expect(screen.getByText('Generate Brand Voice')).toBeInTheDocument();
    expect(screen.getByText('Open Full Generator Interface')).toBeInTheDocument();
  });
  
  test('close button triggers callback', () => {
    const onCloseMock = jest.fn();
    render(<FloatingGeneratorPanel onClose={onCloseMock} />);
    
    // Find and click the close button
    const closeButton = screen.getByRole('button', { name: /close/i });
    fireEvent.click(closeButton);
    
    // Check if the callback is called
    expect(onCloseMock).toHaveBeenCalled();
  });
  
  test('form submission triggers API call', async () => {
    // Mock successful API response
    brandVoiceService.generateBrandVoice.mockResolvedValue({
      success: true,
      brand_voice_components: sampleBrandVoice,
      generation_metadata: { timestamp: '2025-05-24T08:30:00Z', generation_depth: 'basic' }
    });
    
    const onCloseMock = jest.fn();
    render(<FloatingGeneratorPanel onClose={onCloseMock} />);
    
    // Fill the form
    fireEvent.change(screen.getByPlaceholderText(/e.g., Maybelline Singapore/i), {
      target: { value: 'Eco-Friendly Solutions' }
    });
    
    fireEvent.change(screen.getByPlaceholderText(/Paste sample content/i), {
      target: { value: SAMPLE_CONTENT }
    });
    
    // Submit the form
    fireEvent.click(screen.getByText('Generate Brand Voice'));
    
    // Check if the API is called with correct parameters
    expect(brandVoiceService.generateBrandVoice).toHaveBeenCalledWith(
      expect.objectContaining({
        content: SAMPLE_CONTENT,
        brand_name: 'Eco-Friendly Solutions',
        options: expect.objectContaining({
          generation_depth: 'basic',
          include_sample_content: true
        })
      })
    );
    
    // Wait for the result to be displayed
    await waitFor(() => {
      expect(screen.getByText('Generated Brand Voice')).toBeInTheDocument();
    });
  });
});

/**
 * Test the main GeneratorPanel component
 */
describe('GeneratorPanel Component', () => {
  beforeEach(() => {
    // Reset mocks
    jest.clearAllMocks();
  });
  
  test('renders input form correctly', () => {
    render(<GeneratorPanel />);
    
    // Check if form elements are rendered
    expect(screen.getByText('AI Brand Voice Generator')).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/e.g., Maybelline Singapore/i)).toBeInTheDocument();
    expect(screen.getByText('Select Industry')).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/e.g., Women 18-35/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/Paste sample content/i)).toBeInTheDocument();
    expect(screen.getByText('Generate Brand Voice')).toBeInTheDocument();
  });
  
  test('form submission triggers API call and displays result', async () => {
    // Mock successful API responses
    brandVoiceService.generateBrandVoice.mockResolvedValue({
      success: true,
      brand_voice_components: sampleBrandVoice,
      generation_metadata: { timestamp: '2025-05-24T08:30:00Z', generation_depth: 'standard' }
    });
    
    brandVoiceService.saveBrandVoice.mockResolvedValue({
      success: true,
      brand_voice_id: '12345'
    });
    
    render(<GeneratorPanel />);
    
    // Fill the form
    fireEvent.change(screen.getByPlaceholderText(/e.g., Maybelline Singapore/i), {
      target: { value: 'Eco-Friendly Solutions' }
    });
    
    fireEvent.change(screen.getByPlaceholderText(/e.g., Women 18-35/i), {
      target: { value: 'Environmentally conscious consumers' }
    });
    
    fireEvent.change(screen.getByPlaceholderText(/Paste sample content/i), {
      target: { value: SAMPLE_CONTENT }
    });
    
    // Submit the form
    fireEvent.click(screen.getByText('Generate Brand Voice'));
    
    // Check if the API is called with correct parameters
    expect(brandVoiceService.generateBrandVoice).toHaveBeenCalledWith(
      expect.objectContaining({
        content: SAMPLE_CONTENT,
        brand_name: 'Eco-Friendly Solutions',
        target_audience: 'Environmentally conscious consumers',
        options: expect.objectContaining({
          generation_depth: 'standard',
          include_sample_content: true
        })
      })
    );
    
    // Wait for the result to be displayed
    await waitFor(() => {
      expect(screen.getByText('Generated Brand Voice Profile')).toBeInTheDocument();
    });
    
    // Test saving the brand voice
    fireEvent.change(screen.getByPlaceholderText(/Enter a name for this brand voice/i), {
      target: { value: 'Eco-Friendly Brand Voice' }
    });
    
    fireEvent.click(screen.getByText('Save Brand Voice'));
    
    // Check if the save API is called with correct parameters
    expect(brandVoiceService.saveBrandVoice).toHaveBeenCalledWith(
      expect.objectContaining({
        brand_voice_components: sampleBrandVoice,
        name: 'Eco-Friendly Brand Voice'
      })
    );
    
    // Wait for the success message
    await waitFor(() => {
      expect(screen.getByText('Brand Voice Saved Successfully!')).toBeInTheDocument();
    });
  });
});

// If this script is run directly
if (typeof global !== 'undefined' && global.runTests) {
  // This would be implemented differently in a real test environment
  console.log('Running Brand Voice Generator Component Tests');
}
