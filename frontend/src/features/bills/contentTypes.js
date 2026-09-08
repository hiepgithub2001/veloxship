/**
 * Content-line types & the fields each type exposes — single source of truth.
 *
 * To add a new type: append an entry here. It automatically appears in the type
 * selector and renders its fields.
 *   - `value` must also be accepted by the backend (`BillContentLine.cargo_type`).
 *   - `label` is an i18n key from `src/i18n/vi.js`.
 *   - `fields` lists field keys in render order; keys map to `FIELD_DEFS` in
 *     `ContentLineTable.jsx` (unknown keys are ignored).
 * To add a new field: add a `FIELD_DEFS` entry and reference its key here.
 */
export const CONTENT_TYPES = [
  {
    value: 'goods',
    label: 'bills.goods',
    fields: [
      'description',
      'quantity',
      'weight_kg',
      'length_cm',
      'width_cm',
      'height_cm',
      'images',
    ],
  },
  {
    value: 'document',
    label: 'bills.document',
    fields: [
      'description',
      'quantity',
      'weight_kg',
      'length_cm',
      'width_cm',
      'height_cm',
      'images',
    ],
  },
];

// Enum values consumed by `schema.js` (kept in sync with CONTENT_TYPES).
export const CARGO_TYPES = CONTENT_TYPES.map((type) => type.value);
