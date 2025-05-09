// src/utils/format.js

/**
 * Format a date for display
 * @param {string|Date} dateString - Date to format
 * @param {string} format - Optional format specifier
 * @returns {string} Formatted date string
 */
export const formatDate = (dateString, format = 'MMM D, YYYY') => {
  if (!dateString) return 'N/A';

  const date = new Date(dateString);

  // Check for invalid date
  if (isNaN(date.getTime())) return 'Invalid Date';

  // Format based on the specified format
  if (format === 'MMM D') {
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  }
  if (format === 'MMM D, YY') {
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: '2-digit' });
  }

  // Default format: MMM D, YYYY
  return date.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
};

/**
 * Format a number for display with proper thousands separators
 * @param {number} num - Number to format
 * @returns {string} Formatted number string
 */
export const formatNumber = (num) => {
  if (num === undefined || num === null) return 'N/A';

  // For large numbers, abbreviate with K, M, B suffixes
  if (num >= 1000000000) {
    return (num / 1000000000).toFixed(2) + 'B';
  } else if (num >= 1000000) {
    return (num / 1000000).toFixed(2) + 'M';
  } else if (num >= 1000) {
    return (num / 1000).toFixed(2) + 'K';
  }

  // Otherwise, use regular number formatting with commas
  return num.toLocaleString();
};

/**
 * Format a percentage value
 * @param {number} value - Decimal value to format as percentage
 * @returns {string} Formatted percentage string
 */
export const formatPercentage = (value) => {
  if (value === null || value === undefined) return 'N/A';
  return (value * 100).toFixed(1) + '%';
};

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
 * Get the appropriate CSS class for a status chip
 * @param {string} status - Status string
 * @returns {string} CSS class
 */
export const getStatusChipClass = (status) => {
  const classMap = {
    'VERIFIED': 'bg-success/10 text-success',
    'PENDING': 'bg-warning/10 text-warning',
    'FAILED': 'bg-error/10 text-error'
  };
  return classMap[status] || 'bg-gray-100 text-gray-600';
};

/**
 * Get the appropriate icon for a direction
 * @param {string} direction - Direction (UP or DOWN)
 * @returns {string} Icon name
 */
export const getDirectionIcon = (direction) => {
  return direction === 'UP' ? 'mdi-arrow-up-bold' : 'mdi-arrow-down-bold';
};

/**
 * Calculate the date range for a given period
 * @param {string} period - Period specifier (1W, 1M, 3M, 6M, 1Y)
 * @returns {Object} Object with from_date and to_date strings
 */
export const getDateRangeForPeriod = (period) => {
  const today = new Date();
  let fromDate = new Date();

  switch (period) {
    case '1W':
      fromDate.setDate(today.getDate() - 7);
      break;
    case '1M':
      fromDate.setMonth(today.getMonth() - 1);
      break;
    case '3M':
      fromDate.setMonth(today.getMonth() - 3);
      break;
    case '6M':
      fromDate.setMonth(today.getMonth() - 6);
      break;
    case '1Y':
      fromDate.setFullYear(today.getFullYear() - 1);
      break;
    case 'YTD':
      fromDate = new Date(today.getFullYear(), 0, 1); // January 1st of current year
      break;
    default:
      fromDate.setMonth(today.getMonth() - 1); // Default to 1M
  }

  // Format dates as YYYY-MM-DD
  const formatDate = (date) => {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  };

  return {
    from_date: formatDate(fromDate),
    to_date: formatDate(today)
  };
};