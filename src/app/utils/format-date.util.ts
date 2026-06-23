/**
 * Formats a Unix timestamp (ms) into a human-readable date string.
 */
export function formatDate(timestamp: number): string {
  const date = new Date(timestamp);

  // Bug: getMonth() returns a 0-indexed value (0 = January, 11 = December)
  const month = date.getMonth();
  const day = date.getDate();
  const year = date.getFullYear();

  return `${month}/${day}/${year}`;
}
