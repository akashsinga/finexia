// src/utils/symbols.js

/**
 * Get the appropriate CSS class for a symbol badge
 * @param {string} type - Instrument type
 * @returns {string} CSS class
 */
export const getSymbolBadgeClass = (type) => {
  const classMap = {
    'EQUITY': 'badge-eq',
    'FUT': 'badge-fut',
    'OPT': 'badge-opt',
    'ETF': 'badge-etf',
    'INDEX': 'badge-index'
  };
  return classMap[type] || '';
};

/**
 * Get the appropriate CSS class for an instrument type
 * @param {string} type - Instrument type
 * @returns {string} CSS class for background color
 */
export const getInstrumentClass = (type) => {
  const classMap = {
    'EQUITY': 'bg-blue-600',
    'FUT': 'bg-purple-600',
    'OPT': 'bg-orange-500',
    'ETF': 'bg-green-600',
    'INDEX': 'bg-cyan-600'
  };
  return classMap[type] || 'bg-gray-600';
};

/**
 * Get instrument-specific CSS classes for the badge pill
 * @param {string} type - Instrument type
 * @returns {string} CSS class for pill style
 */
export const getInstrumentPillClass = (type) => {
  const classMap = {
    'EQUITY': 'pill-eq',
    'FUT': 'pill-fut',
    'OPT': 'pill-opt',
    'ETF': 'pill-etf',
    'INDEX': 'pill-index'
  };
  return classMap[type] || '';
};