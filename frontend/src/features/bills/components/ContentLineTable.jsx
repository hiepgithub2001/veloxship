/**
 * Content line — one compact block per line.
 *
 * Layout:
 *   A numbered badge sits in the card's corner; the Loại hàng (type) selector
 *   spans the full width on the same row as the duplicate / delete / drag handle.
 *   The selected type's fields render below — only after a type is chosen.
 *
 * Extensibility — add a type without touching this layout:
 *   - `contentTypes.js` (`CONTENT_TYPES`) is the single source of truth for the
 *     list of types and which fields each shows, in order.
 *   - `FIELD_DEFS` below maps a field key → label + renderer. To add a field,
 *     add an entry here and reference its key in the type's `fields` list.
 *   Custom per-type fields can read/write the line's `metadata` blob.
 */
import { Button, Card, Input, InputNumber, Select, Tooltip, Typography } from 'antd';
import { CopyOutlined, DeleteOutlined, HolderOutlined } from '@ant-design/icons';
import ImageUpload from '../../../components/common/ImageUpload';
import { t } from '../../../i18n/vi';
import { CONTENT_TYPES } from '../contentTypes';
import { brandColors } from '../../../styles/theme';

const { Text } = Typography;

const labelStyle = {
  display: 'block',
  fontSize: 12,
  color: '#8c8c8c',
  marginBottom: 2,
  whiteSpace: 'nowrap',
};

function Field({ label, style, children }) {
  return (
    <div style={style}>
      <Text style={labelStyle}>{label}</Text>
      {children}
    </div>
  );
}

// Reusable renderer for the three dimension inputs (Dài / Rộng / Cao).
function dimField(key, label) {
  return {
    label,
    width: { width: 72 },
    render: ({ index, watch, setValue }) => (
      <InputNumber
        min={0}
        step={0.1}
        decimalSeparator=","
        value={watch(`contents.${index}.${key}`)}
        onChange={(val) => setValue(`contents.${index}.${key}`, val)}
        style={{ width: '100%' }}
      />
    ),
  };
}

// Every field a content line can expose, keyed by the values used in CONTENT_TYPES.
const FIELD_DEFS = {
  description: {
    label: 'bills.description',
    width: { flex: 1, minWidth: 160 },
    render: ({ index, watch, setValue }) => (
      <Input.TextArea
        rows={2}
        value={watch(`contents.${index}.description`)}
        onChange={(e) => setValue(`contents.${index}.description`, e.target.value)}
        placeholder={t('bills.description')}
        id={`content-${index}-description`}
      />
    ),
  },
  quantity: {
    label: 'bills.quantity',
    width: { width: 72 },
    render: ({ index, watch, setValue }) => (
      <InputNumber
        min={1}
        value={watch(`contents.${index}.quantity`)}
        onChange={(val) => setValue(`contents.${index}.quantity`, val)}
        style={{ width: '100%' }}
        id={`content-${index}-quantity`}
      />
    ),
  },
  weight_kg: {
    label: 'bills.weight',
    width: { width: 100 },
    render: ({ index, watch, setValue }) => (
      <InputNumber
        min={0}
        step={0.01}
        decimalSeparator=","
        value={watch(`contents.${index}.weight_kg`)}
        onChange={(val) => setValue(`contents.${index}.weight_kg`, val)}
        style={{ width: '100%' }}
        id={`content-${index}-weight`}
      />
    ),
  },
  length_cm: dimField('length_cm', 'bills.length'),
  width_cm: dimField('width_cm', 'bills.width'),
  height_cm: dimField('height_cm', 'bills.height'),
  images: {
    label: 'bills.images',
    width: { flexShrink: 0 },
    render: ({ index, watch, setValue }) => (
      <ImageUpload
        value={watch(`contents.${index}.images`) || []}
        onChange={(val) => setValue(`contents.${index}.images`, val)}
        maxCount={3}
      />
    ),
  },
};

export function ContentLineTable({
  index,
  canRemove,
  onRemove,
  onDuplicate,
  setValue,
  watch,
  dragHandleProps,
  onDragOver,
  onDrop,
  isDragOver,
}) {
  const cargoType = watch(`contents.${index}.cargo_type`);
  const selectedType = CONTENT_TYPES.find((type) => type.value === cargoType);
  const typeOptions = CONTENT_TYPES.map((type) => ({ value: type.value, label: t(type.label) }));

  return (
    <div
      onDragOver={onDragOver}
      onDrop={onDrop}
      style={{
        position: 'relative',
        marginBottom: 12,
        outline: isDragOver ? `2px dashed ${brandColors.primary}` : undefined,
        outlineOffset: 2,
        borderRadius: 6,
      }}
    >
      <span
        style={{
          position: 'absolute',
          top: -10,
          left: -10,
          zIndex: 2,
          minWidth: 22,
          height: 22,
          padding: '0 6px',
          borderRadius: 11,
          background: brandColors.primary,
          color: '#fff',
          fontSize: 12,
          fontWeight: 600,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          boxShadow: '0 1px 3px rgba(0, 0, 0, 0.25)',
        }}
      >
        {index + 1}
      </span>

      <Card size="small" styles={{ body: { padding: 12 } }}>
        {/* header row — type (full width) + duplicate / delete / drag handle */}
        <div
          style={{
            display: 'flex',
            gap: 8,
            alignItems: 'center',
            marginBottom: selectedType ? 8 : 0,
          }}
        >
          <Button
            type="text"
            icon={<HolderOutlined />}
            draggable
            {...dragHandleProps}
            style={{ cursor: 'grab', color: '#8c8c8c' }}
            aria-label={t('bills.drag')}
          />
          <Select
            value={cargoType}
            onChange={(val) => setValue(`contents.${index}.cargo_type`, val)}
            placeholder={t('bills.cargoType')}
            style={{ flex: 1 }}
            options={typeOptions}
            id={`content-${index}-cargo-type`}
          />
          <Tooltip title={t('bills.duplicateLine')}>
            <Button
              type="text"
              icon={<CopyOutlined />}
              onClick={onDuplicate}
              id={`content-${index}-duplicate`}
            />
          </Tooltip>
          {canRemove && (
            <Tooltip title={t('bills.removeLine')}>
              <Button
                type="text"
                danger
                icon={<DeleteOutlined />}
                onClick={onRemove}
                id={`content-${index}-remove`}
              />
            </Tooltip>
          )}
        </div>

        {/* the selected type's fields (appear after a type is chosen) */}
        {selectedType && (
          <div style={{ display: 'flex', gap: 8, alignItems: 'center', flexWrap: 'wrap' }}>
            {selectedType.fields.map((key) => {
              const def = FIELD_DEFS[key];
              if (!def) return null;
              return (
                <Field key={key} label={t(def.label)} style={def.width}>
                  {def.render({ index, watch, setValue })}
                </Field>
              );
            })}
          </div>
        )}
      </Card>
    </div>
  );
}

export default ContentLineTable;
