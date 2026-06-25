/**
 * Formats a Unix timestamp (ms) into a human-readable date string.
 */
export function formatDate(timestamp: number): string {
  const date = new Date(timestamp);

  const month = date.getMonth() + 1;
  const day = date.getDate();
  const year = date.getFullYear();

  return `${month}/${day}/${year}`;
}
