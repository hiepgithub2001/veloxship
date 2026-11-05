/**
 * Status → colour/label maps for the Excel import module.
 *
 * Colours are Ant Design preset palette names (the same convention as the bill
 * status tags in `features/bills`): the Tag component itself is themed by
 * `AntdConfigProvider`, so no brand colour is hard-coded here.
 */
import { t } from '../../i18n/vi';

export const IMPORT_ROW_STATUS_COLORS = {
  ok: 'green',
  warning: 'gold',
  error: 'red',
  imported: 'blue',
  skipped: 'default',
};

export const IMPORT_BATCH_STATUS_COLORS = {
  validating: 'processing',
  validated: 'blue',
  committing: 'processing',
  completed: 'green',
  partially_completed: 'gold',
  failed: 'red',
};

/** Vietnamese label for an import row status; unknown statuses fall back to the raw value. */
export function importRowStatusLabel(status) {
  const key = `imports.rowStatus.${status}`;
  const label = t(key);
  return label === key ? status || '—' : label;
}

/** Vietnamese label for an import batch status; unknown statuses fall back to the raw value. */
export function importBatchStatusLabel(status) {
  const key = `imports.batchStatus.${status}`;
  const label = t(key);
  return label === key ? status || '—' : label;
}
