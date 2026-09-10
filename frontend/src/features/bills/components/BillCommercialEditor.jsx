import { useEffect, useState } from 'react';
import { Button, InputNumber, Space, Table, Tag } from 'antd';
import { SaveOutlined } from '@ant-design/icons';
import { useFieldArray, useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { ContentTable } from './ContentTable';
import { CONTENT_TYPES } from '../contentTypes';
import { contentLineSchema } from '../schema';
import { ImagePreviewGroup } from '../../../components/common/ImagePreviewGroup';
import { t } from '../../../i18n/vi';

const commercialSchema = z.object({
  contents: z.array(contentLineSchema).min(1, 'Phiếu gửi phải có ít nhất một dòng nội dung.'),
  cod_amount: z.number().min(0, 'Giá trị không được âm.'),
});

const toEditableLine = ({ line_no, ...line }) => line;

const formatMetadataLabel = (key) => key.replace(/_/g, ' ').replace(/^./, (letter) => letter.toUpperCase());
const formatMetadata = (metadata) =>
  Object.entries(metadata || {})
    .filter(([, value]) => value != null && value !== '')
    .map(([key, value]) => `${formatMetadataLabel(key)}: ${typeof value === 'object' ? JSON.stringify(value) : value}`)
    .join(' · ') || '—';

/** Draft-only editor that reuses the content-line form from bill creation. */
export function BillCommercialEditor({ bill, saving, onSave }) {
  const [editing, setEditing] = useState(false);
  const {
    control,
    getValues,
    handleSubmit,
    reset,
    setValue,
    watch,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(commercialSchema),
    defaultValues: { contents: [], cod_amount: 0 },
  });
  const { fields, append, insert, move, remove } = useFieldArray({ control, name: 'contents' });

  useEffect(() => {
    reset({
      contents: bill.contents.map(toEditableLine),
      cod_amount: bill.cod_amount,
    });
  }, [bill, reset]);

  const columns = [
    { title: '#', width: 48, render: (_, __, index) => index + 1 },
    {
      title: t('bills.cargoType'),
      width: 112,
      render: (_, line) => {
        const cargoType = CONTENT_TYPES.find((type) => type.value === line.cargo_type);
        return <Tag color="blue">{t(cargoType?.label || 'bills.goods')}</Tag>;
      },
    },
    { title: t('bills.description'), dataIndex: 'description', ellipsis: true },
    { title: t('bills.quantity'), dataIndex: 'quantity', width: 74, align: 'center' },
    {
      title: t('bills.weight'),
      width: 100,
      render: (_, line) => `${line.weight_kg} kg`,
    },
    {
      title: 'Kích thước',
      width: 150,
      render: (_, line) => {
        const dimensions = [line.length_cm, line.width_cm, line.height_cm];
        return dimensions.every((value) => value != null) ? `${dimensions.join(' × ')} cm` : '—';
      },
    },
    {
      title: t('bills.images'),
      width: 72,
      render: (_, line) => <ImagePreviewGroup images={line.images} />,
    },
    {
      title: 'Thông tin thêm',
      width: 190,
      render: (_, line) => <span className="bill-content-metadata">{formatMetadata(line.metadata)}</span>,
    },
  ];

  const save = ({ contents, cod_amount: codAmount }) => {
    onSave({ contents, cod_amount: codAmount });
    setEditing(false);
  };
  return (
    <div className="bill-commercial-editor">
      <div className="bill-block-heading">
        <div>
          <h3>{t('bills.cargoInfo')}</h3>
          <span>Nội dung hàng hóa và tiền thu hộ</span>
        </div>
        {bill.status === 'created' && !editing && (
          <Button onClick={() => setEditing(true)}>Chỉnh sửa</Button>
        )}
      </div>
      {editing ? (
        <ContentTable
          fields={fields}
          append={append}
          remove={remove}
          move={move}
          insert={insert}
          getValues={getValues}
          setValue={setValue}
          watch={watch}
        />
      ) : (
        <Table
          className="bill-content-summary-table"
          size="small"
          rowKey={(line, index) => line.line_no || index}
          pagination={false}
          dataSource={bill.contents}
          columns={columns}
        />
      )}
      {editing && errors.contents && (
        <div style={{ color: '#ff4d4f', marginTop: 8 }}>
          {errors.contents.message || errors.contents.root?.message}
        </div>
      )}
      <div className="bill-cod-row">
        <strong>{t('bills.codAmount')}</strong>
        {editing ? (
          <InputNumber
            min={0}
            value={watch('cod_amount')}
            onChange={(value) => setValue('cod_amount', value || 0)}
            formatter={(v) => `${v}`.replace(/\B(?=(\d{3})+(?!\d))/g, '.')}
            parser={(v) => v.replace(/\./g, '')}
            addonAfter="₫"
          />
        ) : (
          <strong>
            {new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(
              bill.cod_amount,
            )}
          </strong>
        )}
      </div>
      {editing && (
        <Space style={{ marginTop: 14 }}>
          <Button type="primary" icon={<SaveOutlined />} loading={saving} onClick={handleSubmit(save)}>
            {t('common.save')}
          </Button>
          <Button
            onClick={() => {
              reset({
                contents: bill.contents.map(toEditableLine),
                cod_amount: bill.cod_amount,
              });
              setEditing(false);
            }}
          >
            {t('common.cancel')}
          </Button>
        </Space>
      )}
    </div>
  );
}
