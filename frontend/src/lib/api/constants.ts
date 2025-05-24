/**
 * API Constants
 * This file contains constants used across API services
 */

// Development token for testing
// In production, this would be fetched from a secure authentication service
export const DEV_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyLTEyMyIsInRlbmFudF9pZCI6InRlbmFudC0xMjMiLCJyb2xlIjoiYWRtaW4iLCJleHAiOjE3NDc5NzcxNzV9.iRGPvHgK3GaH3ZDwgbfpZBgOhCCYe7pLRl3c1YROj6c';

// Default headers for API requests
export const DEFAULT_HEADERS = {
  'Content-Type': 'application/json',
  'Authorization': `Bearer ${DEV_TOKEN}`
};

// Request timeout in milliseconds
export const REQUEST_TIMEOUT = 30000; // 30 seconds
