/**
 * Content table — editable, sortable list of content lines (one card per line).
 */
import { useRef, useState } from 'react';
import { Button } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import { ContentLineTable } from './ContentLineTable';
import { t } from '../../../i18n/vi';

export function ContentTable({ fields, append, remove, move, insert, getValues, setValue, watch }) {
  const dragIndex = useRef(null);
  const [overIndex, setOverIndex] = useState(null);

  const handleDragStart = (index) => (event) => {
    dragIndex.current = index;
    event.dataTransfer.effectAllowed = 'move';
    // Firefox requires data to be set before it will start a drag.
    event.dataTransfer.setData('text/plain', String(index));
  };

  const handleDragOver = (index) => (event) => {
    event.preventDefault();
    setOverIndex(index);
  };

  const handleDrop = (index) => (event) => {
    event.preventDefault();
    const from = dragIndex.current;
    if (from !== null && from !== index) {
      move(from, index);
    }
    dragIndex.current = null;
    setOverIndex(null);
  };

  const handleDragEnd = () => {
    dragIndex.current = null;
    setOverIndex(null);
  };

  const duplicateLine = (index) => {
    const line = getValues(`contents.${index}`);
    insert(index + 1, JSON.parse(JSON.stringify(line)));
  };

  return (
    <div>
      <h4 className="form-section-title">{t('bills.contents')}</h4>

      {fields.map((field, index) => (
        <ContentLineTable
          key={field.id}
          index={index}
          canRemove={fields.length > 1}
          onRemove={() => remove(index)}
          onDuplicate={() => duplicateLine(index)}
          setValue={setValue}
          watch={watch}
          dragHandleProps={{
            onDragStart: handleDragStart(index),
            onDragEnd: handleDragEnd,
          }}
          onDragOver={handleDragOver(index)}
          onDrop={handleDrop(index)}
          isDragOver={overIndex === index}
        />
      ))}

      <Button
        type="dashed"
        icon={<PlusOutlined />}
        onClick={() =>
          append({ cargo_type: 'goods', description: '', quantity: 1, weight_kg: 0, length_cm: null, width_cm: null, height_cm: null, images: [], metadata: {} })
        }
        style={{ marginTop: 8, width: '100%' }}
        id="add-content-line"
      >
        {t('bills.addLine')}
      </Button>
    </div>
  );
}

export default ContentTable;
