/**
 * Shared bill-status vocabulary — order, Ant Design tag colours, and chart hex.
 *
 * Kept in `lib/` (not inside `features/bills`) so the dashboard can colour its
 * status charts with the same palette without importing across features.
 */

export const BILL_STATUS_ORDER = [
  'created',
  'picked_up',
  'in_transit',
  'delivered',
  'returned',
  'cancelled',
];

/** Ant Design Tag colour names (used by the bill table). */
export const BILL_STATUS_COLORS = {
  created: 'blue',
  picked_up: 'cyan',
  in_transit: 'orange',
  delivered: 'green',
  returned: 'purple',
  cancelled: 'red',
};

/** Hex values for charts (status pie, etc.). */
export const BILL_STATUS_HEX = {
  created: '#1890FF',
  picked_up: '#13C2C2',
  in_transit: '#FAAD14',
  delivered: '#52C41A',
  returned: '#722ED1',
  cancelled: '#FF4D4F',
};
