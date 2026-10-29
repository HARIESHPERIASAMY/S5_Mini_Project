/**
 * SentinelMesh Release Gate Threshold Constants
 * 
 * Centralized governance metrics determining production readiness:
 * - MIN_COVERAGE: 80% code coverage across all audited statements
 * - MIN_MUTATION: 60% mutant survival kill rate via AST mutation
 * - MIN_SUITE_HEALTH: 75/100 composite health index
 * - MAX_OPEN_CRITICAL: 0 unresolved critical severity defects allowed
 * - ALL_FIXES_VERIFIED: All detected bugs must have sandboxed passing patches
 */
export const RELEASE_GATE_THRESHOLDS = {
  MIN_COVERAGE: 80,       // Minimum code coverage percentage
  MIN_MUTATION: 60,       // Minimum mutation kill score percentage
  MIN_SUITE_HEALTH: 75,   // Minimum suite health score (0 - 100)
  MAX_OPEN_CRITICAL: 0,   // Zero open critical defects tolerated
  ALL_FIXES_VERIFIED: true
};

