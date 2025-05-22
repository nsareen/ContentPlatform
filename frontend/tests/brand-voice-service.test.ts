import { brandVoiceService, BrandVoiceUpdateRequest } from '../src/lib/api/brand-voice-service';
import authService from '../src/lib/auth/auth-service';

// Mock the auth service
jest.mock('../src/lib/auth/auth-service', () => ({
  makeAuthenticatedRequest: jest.fn(),
  getAuthToken: jest.fn().mockResolvedValue('mock-token')
}));

// Mock fetch for direct request fallback testing
global.fetch = jest.fn();
global.XMLHttpRequest = jest.fn().mockImplementation(() => ({
  open: jest.fn(),
  send: jest.fn(),
  setRequestHeader: jest.fn(),
  onload: jest.fn(),
  onerror: jest.fn(),
  ontimeout: jest.fn(),
  responseText: '{"id":"123","name":"Test Voice"}',
  status: 200
}));

describe('Brand Voice Service', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    console.log = jest.fn();
    console.error = jest.fn();
  });

  describe('updateBrandVoice', () => {
    const mockVoice = { id: '123', name: 'Test Voice', description: 'Test Description' };
    const updateData: BrandVoiceUpdateRequest = { name: 'Updated Voice' };

    it('should successfully update a brand voice', async () => {
      // Mock successful response
      (authService.makeAuthenticatedRequest as jest.Mock).mockResolvedValueOnce(mockVoice);

      const result = await brandVoiceService.updateBrandVoice('123', updateData);
      
      expect(result).toEqual(mockVoice);
      expect(authService.makeAuthenticatedRequest).toHaveBeenCalledTimes(1);
      expect(authService.makeAuthenticatedRequest).toHaveBeenCalledWith(
        expect.stringContaining('/voices/123'),
        'PUT',
        updateData,
        expect.any(Object)
      );
    });

    it('should retry on network failure', async () => {
      // Mock network failures followed by success
      (authService.makeAuthenticatedRequest as jest.Mock)
        .mockRejectedValueOnce(new Error('Network error'))
        .mockRejectedValueOnce(new Error('Network error'))
        .mockResolvedValueOnce(mockVoice);

      const result = await brandVoiceService.updateBrandVoice('123', updateData);
      
      expect(result).toEqual(mockVoice);
      expect(authService.makeAuthenticatedRequest).toHaveBeenCalledTimes(3);
    });

    it('should use direct XMLHttpRequest as fallback when primary request fails', async () => {
      // Mock primary request failure
      (authService.makeAuthenticatedRequest as jest.Mock).mockRejectedValue(new Error('Primary request failed'));
      
      // Setup XMLHttpRequest mock to simulate success
      const xhrMock = {
        open: jest.fn(),
        send: jest.fn(),
        setRequestHeader: jest.fn(),
        status: 200,
        responseText: JSON.stringify(mockVoice),
        onload: null,
        onerror: null,
        ontimeout: null
      };
      
      (global.XMLHttpRequest as jest.Mock).mockImplementation(() => {
        setTimeout(() => {
          if (xhrMock.onload) xhrMock.onload();
        }, 10);
        return xhrMock;
      });

      const result = await brandVoiceService.updateBrandVoice('123', updateData);
      
      // Verify the result matches our mock
      expect(result).toEqual(mockVoice);
      
      // Verify primary request was attempted
      expect(authService.makeAuthenticatedRequest).toHaveBeenCalledTimes(1);
    });

    it('should throw enhanced error after max retries', async () => {
      // Mock consistent failures
      const networkError = new Error('Network error');
      (authService.makeAuthenticatedRequest as jest.Mock).mockRejectedValue(networkError);
      
      // Setup XMLHttpRequest mock to simulate failure
      const xhrMock = {
        open: jest.fn(),
        send: jest.fn(),
        setRequestHeader: jest.fn(),
        onerror: null
      };
      
      (global.XMLHttpRequest as jest.Mock).mockImplementation(() => {
        setTimeout(() => {
          if (xhrMock.onerror) xhrMock.onerror();
        }, 10);
        return xhrMock;
      });

      await expect(brandVoiceService.updateBrandVoice('123', updateData))
        .rejects.toThrow(/Failed to update brand voice after \d+ attempts/);
      
      // Verify we attempted the expected number of retries
      expect(authService.makeAuthenticatedRequest).toHaveBeenCalledTimes(4); // Initial + 3 retries
    });
  });
});
