/**
 * Vietnamese formatting helpers.
 */

/**
 * Format a number as VND currency.
 * @param {number} n
 * @returns {string} e.g. "1.500.000 ₫"
 */
export function formatVND(n) {
  if (n == null) return '';
  return new Intl.NumberFormat('vi-VN', {
    style: 'currency',
    currency: 'VND',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(n);
}

/**
 * Format weight in kg with Vietnamese comma decimal.
 * @param {number} n
 * @returns {string} e.g. "200,00 kg"
 */
export function formatWeight(n) {
  if (n == null) return '';
  return `${new Intl.NumberFormat('vi-VN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 3,
  }).format(n)} kg`;
}

/**
 * Format a date in Vietnamese style.
 * @param {string|Date} d
 * @returns {string} e.g. "26/04/2026"
 */
export function formatViDate(d) {
  if (!d) return '';
  const date = new Date(d);
  return new Intl.DateTimeFormat('vi-VN', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    timeZone: 'Asia/Ho_Chi_Minh',
  }).format(date);
}

/**
 * Format a date+time in Vietnamese style.
 * @param {string|Date} d
 * @returns {string} e.g. "26/04/2026 17:30"
 */
export function formatViDateTime(d) {
  if (!d) return '';
  const date = new Date(d);
  return new Intl.DateTimeFormat('vi-VN', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    timeZone: 'Asia/Ho_Chi_Minh',
  }).format(date);
}

/**
 * Parse a Vietnamese-formatted number string (comma decimal → dot decimal).
 * @param {string} str e.g. "200,00"
 * @returns {number} e.g. 200.00
 */
export function parseViNumber(str) {
  if (!str) return 0;
  // Remove thousand separators (dots), replace comma decimal with dot
  return parseFloat(String(str).replace(/\./g, '').replace(',', '.')) || 0;
}
