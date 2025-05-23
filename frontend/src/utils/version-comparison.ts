/**
 * Version Comparison Utilities
 * 
 * This file contains utility functions for comparing brand voice versions
 */

import { 
  BrandVoiceVersion, 
  VersionComparison, 
  VersionDiff,
  ChangeType
} from '@/types/brand-voice';
import { BRAND_VOICE_CONFIG } from '@/config/brand-voice-config';

/**
 * Get a nested property value from an object using a dot-notation path
 */
function getNestedValue(obj: any, path: string): any {
  const keys = path.split('.');
  return keys.reduce((value, key) => 
    (value && value[key] !== undefined) ? value[key] : undefined, 
    obj
  );
}

/**
 * Get the display name for a field based on the configuration
 */
function getFieldDisplayName(field: string): string {
  const fieldConfig = BRAND_VOICE_CONFIG.COMPARABLE_FIELDS.find(f => f.key === field);
  return fieldConfig ? fieldConfig.label : field;
}

/**
 * Determine the type of change between two values
 */
function determineChangeType(oldValue: any, newValue: any): ChangeType {
  if (oldValue === undefined || oldValue === null) {
    return 'added';
  }
  
  if (newValue === undefined || newValue === null) {
    return 'removed';
  }
  
  if (oldValue === newValue) {
    return 'unchanged';
  }
  
  return 'modified';
}

/**
 * Compare two brand voice versions and generate a detailed comparison
 */
export function compareVersions(
  baseVersion: BrandVoiceVersion,
  comparedVersion: BrandVoiceVersion
): VersionComparison {
  const differences: VersionDiff[] = [];
  
  // Get the fields to compare from the configuration
  const fieldsToCompare = BRAND_VOICE_CONFIG.COMPARABLE_FIELDS.map(f => f.key);
  
  // Compare each field
  fieldsToCompare.forEach(field => {
    const oldValue = getNestedValue(baseVersion, field);
    const newValue = getNestedValue(comparedVersion, field);
    const changeType = determineChangeType(oldValue, newValue);
    
    // Only add to differences if there's a change
    if (changeType !== 'unchanged') {
      differences.push({
        field,
        oldValue,
        newValue,
        changeType,
        displayName: getFieldDisplayName(field)
      });
    }
  });
  
  return {
    baseVersion,
    comparedVersion,
    differences
  };
}

/**
 * Format a value for display in the comparison UI
 */
export function formatValueForDisplay(value: any, field: string): string {
  if (value === undefined || value === null) {
    return '—';
  }
  
  if (field === 'status') {
    return value.charAt(0).toUpperCase() + value.slice(1);
  }
  
  if (typeof value === 'object') {
    return JSON.stringify(value, null, 2);
  }
  
  return String(value);
}

/**
 * Get the background color for a change type
 */
export function getChangeColor(changeType: ChangeType): string {
  // Convert the change type to uppercase and cast as a key of DIFF_COLORS
  const colorKey = changeType.toUpperCase() as keyof typeof BRAND_VOICE_CONFIG.VERSION_COMPARISON.DIFF_COLORS;
  return BRAND_VOICE_CONFIG.VERSION_COMPARISON.DIFF_COLORS[colorKey] || 
         BRAND_VOICE_CONFIG.VERSION_COMPARISON.DIFF_COLORS.UNCHANGED;
}

/**
 * Check if two versions are different
 */
export function areVersionsDifferent(
  baseVersion: BrandVoiceVersion,
  comparedVersion: BrandVoiceVersion
): boolean {
  const comparison = compareVersions(baseVersion, comparedVersion);
  return comparison.differences.length > 0;
}

/**
 * Get a summary of changes between versions
 */
export function getVersionChangeSummary(
  baseVersion: BrandVoiceVersion,
  comparedVersion: BrandVoiceVersion
): string {
  const comparison = compareVersions(baseVersion, comparedVersion);
  
  if (comparison.differences.length === 0) {
    return 'No changes';
  }
  
  const changedFields = comparison.differences.map(diff => diff.displayName);
  
  if (changedFields.length <= 2) {
    return `Changed: ${changedFields.join(', ')}`;
  }
  
  return `Changed ${changedFields.length} fields`;
}
