/**
 * Common utility functions for the Finexia application
 */

/**
 * Format date string to specified format
 * @param {string} dateString - Date string to format
 * @param {string} format - Optional format (simplified version, actual formatting handled by Date methods)
 * @returns {string} Formatted date string
 */
export const formatDate = (dateString, format = 'MMM D, YYYY') => {
  if (!dateString) return 'N/A';

  const date = new Date(dateString);

  // Format options based on the requested format
  const options = {
    month: 'short',
    day: 'numeric'
  };

  if (format.includes('YYYY') || format.includes('yyyy')) {
    options.year = 'numeric';
  }

  if (format.includes('HH') || format.includes('hh')) {
    options.hour = '2-digit';
    options.minute = '2-digit';
  }

  return date.toLocaleDateString('en-US', options);
};

/**
 * Format number with commas (e.g. 1,234,567)
 * @param {number} num - Number to format
 * @returns {string} Formatted number
 */
export const formatNumber = (num) => {
  if (num === null || num === undefined) return 'N/A';
  return new Intl.NumberFormat('en-IN').format(num);
};

/**
 * Format percentage value
 * @param {number} value - Value between 0 and 1
 * @returns {string} Formatted percentage
 */
export const formatPercentage = (value) => {
  if (value === null || value === undefined) return 'N/A';
  return (value * 100).toFixed(1) + '%';
};

/**
 * Get CSS class for a symbol badge based on instrument type
 * @param {string} type - Instrument type
 * @returns {string} CSS class name
 */
export const getSymbolBadgeClass = (type) => {
  const classes = {
    'EQUITY': 'bg-blue-600',
    'FUT': 'bg-purple-600',
    'OPT': 'bg-orange-500',
    'ETF': 'bg-green-600',
    'INDEX': 'bg-cyan-600'
  };
  return classes[type] || 'bg-gray-500';
};

/**
 * Get CSS class for instrument type
 * @param {string} type - Instrument type
 * @returns {string} CSS class for styling
 */
export const getInstrumentClass = (type) => {
  const classes = {
    'EQUITY': 'bg-blue-600',
    'FUT': 'bg-purple-600',
    'OPT': 'bg-orange-500',
    'ETF': 'bg-green-600',
    'INDEX': 'bg-cyan-600'
  };
  return classes[type] || 'bg-gray-500';
};

/**
 * Get CSS class for status chip
 * @param {string} status - Status value
 * @returns {string} CSS class
 */
export const getStatusChipClass = (status) => {
  if (status === 'VERIFIED') return 'bg-green-100 text-green-700';
  if (status === 'FAILED') return 'bg-red-100 text-red-700';
  if (status === 'PENDING') return 'bg-yellow-100 text-yellow-700';
  return 'bg-gray-100 text-gray-700';
};

/**
 * Get direction icon name based on direction value
 * @param {string} direction - Direction (UP or DOWN)
 * @returns {string} Icon name
 */
export const getDirectionIcon = (direction) => {
  return direction === 'UP' ? 'mdi-arrow-up-bold' : 'mdi-arrow-down-bold';
};

/**
 * Calculate date range for chart periods
 * @param {string} period - Period value (1W, 1M, 3M, 6M, 1Y)
 * @returns {Object} Object with from_date and to_date in YYYY-MM-DD format
 */
export const getDateRangeForPeriod = (period) => {
  const to_date = new Date();
  let from_date = new Date();

  switch (period) {
    case '1W':
      from_date.setDate(to_date.getDate() - 7);
      break;
    case '1M':
      from_date.setMonth(to_date.getMonth() - 1);
      break;
    case '3M':
      from_date.setMonth(to_date.getMonth() - 3);
      break;
    case '6M':
      from_date.setMonth(to_date.getMonth() - 6);
      break;
    case '1Y':
      from_date.setFullYear(to_date.getFullYear() - 1);
      break;
    default:
      from_date.setMonth(to_date.getMonth() - 1); // Default to 1M
  }

  // Format as YYYY-MM-DD
  const format = (date) => {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  };

  return {
    from_date: format(from_date),
    to_date: format(to_date)
  };
};