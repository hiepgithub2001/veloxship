/**
 * Content table — editable list of content lines.
 */
import { Button, InputNumber, Input, Table, Space } from 'antd';
import { PlusOutlined, DeleteOutlined } from '@ant-design/icons';
import { t } from '../../../i18n/vi';

export function ContentTable({ fields, append, remove, setValue, watch }) {
  const columns = [
    {
      title: '#',
      width: 50,
      render: (_, __, index) => index + 1,
    },
    {
      title: t('bills.description'),
      dataIndex: 'description',
      render: (_, __, index) => (
        <Input
          value={watch(`contents.${index}.description`)}
          onChange={(e) => setValue(`contents.${index}.description`, e.target.value)}
          placeholder={t('bills.description')}
          id={`content-${index}-description`}
        />
      ),
    },
    {
      title: t('bills.quantity'),
      width: 100,
      render: (_, __, index) => (
        <InputNumber
          min={1}
          value={watch(`contents.${index}.quantity`)}
          onChange={(val) => setValue(`contents.${index}.quantity`, val)}
          style={{ width: '100%' }}
          id={`content-${index}-quantity`}
        />
      ),
    },
    {
      title: t('bills.weight'),
      width: 130,
      render: (_, __, index) => (
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
    {
      title: t('bills.length'),
      width: 90,
      render: (_, __, index) => (
        <InputNumber
          min={0}
          step={0.1}
          decimalSeparator=","
          value={watch(`contents.${index}.length_cm`)}
          onChange={(val) => setValue(`contents.${index}.length_cm`, val)}
          style={{ width: '100%' }}
        />
      ),
    },
    {
      title: t('bills.width'),
      width: 90,
      render: (_, __, index) => (
        <InputNumber
          min={0}
          step={0.1}
          decimalSeparator=","
          value={watch(`contents.${index}.width_cm`)}
          onChange={(val) => setValue(`contents.${index}.width_cm`, val)}
          style={{ width: '100%' }}
        />
      ),
    },
    {
      title: t('bills.height'),
      width: 90,
      render: (_, __, index) => (
        <InputNumber
          min={0}
          step={0.1}
          decimalSeparator=","
          value={watch(`contents.${index}.height_cm`)}
          onChange={(val) => setValue(`contents.${index}.height_cm`, val)}
          style={{ width: '100%' }}
        />
      ),
    },
    {
      title: '',
      width: 50,
      render: (_, __, index) =>
        fields.length > 1 && (
          <Button
            type="text"
            danger
            icon={<DeleteOutlined />}
            onClick={() => remove(index)}
            id={`content-${index}-remove`}
          />
        ),
    },
  ];

  return (
    <div>
      <h4 style={{ color: '#C41E3A', marginBottom: 8 }}>{t('bills.contents')}</h4>
      <Table
        dataSource={fields}
        columns={columns}
        pagination={false}
        rowKey="id"
        size="small"
        bordered
      />
      <Button
        type="dashed"
        icon={<PlusOutlined />}
        onClick={() =>
          append({ description: '', quantity: 1, weight_kg: 0, length_cm: null, width_cm: null, height_cm: null })
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
