import { useEffect, useState } from 'react';
import { Button, Input, InputNumber, Space, Table } from 'antd';
import { DeleteOutlined, PlusOutlined, SaveOutlined } from '@ant-design/icons';
import { t } from '../../../i18n/vi';

const emptyLine = () => ({
  cargo_type: 'goods',
  description: '',
  quantity: 1,
  weight_kg: 0,
  length_cm: null,
  width_cm: null,
  height_cm: null,
  images: [],
  metadata: {},
});

/** Inline, draft-only editor for the parts most often corrected at the counter. */
export function BillCommercialEditor({ bill, saving, onSave }) {
  const [editing, setEditing] = useState(false);
  const [contents, setContents] = useState([]);
  const [codAmount, setCodAmount] = useState(0);
  useEffect(() => {
    setContents(bill.contents.map((line) => ({ ...line })));
    setCodAmount(bill.cod_amount);
  }, [bill]);
  const updateLine = (index, field, value) =>
    setContents((items) =>
      items.map((item, i) => (i === index ? { ...item, [field]: value } : item)),
    );
  const columns = [
    { title: '#', width: 44, render: (_, __, index) => index + 1 },
    {
      title: t('bills.description'),
      dataIndex: 'description',
      render: (value, _, index) =>
        editing ? (
          <Input value={value} onChange={(e) => updateLine(index, 'description', e.target.value)} />
        ) : (
          value
        ),
    },
    {
      title: t('bills.quantity'),
      dataIndex: 'quantity',
      width: 100,
      render: (value, _, index) =>
        editing ? (
          <InputNumber
            min={1}
            value={value}
            onChange={(v) => updateLine(index, 'quantity', v || 1)}
          />
        ) : (
          value
        ),
    },
    {
      title: 'Kích thước (cm)',
      width: 230,
      render: (_, row, index) =>
        editing ? (
          <Space.Compact>
            <InputNumber
              min={0}
              value={row.length_cm}
              placeholder="D"
              onChange={(v) => updateLine(index, 'length_cm', v)}
            />
            <InputNumber
              min={0}
              value={row.width_cm}
              placeholder="R"
              onChange={(v) => updateLine(index, 'width_cm', v)}
            />
            <InputNumber
              min={0}
              value={row.height_cm}
              placeholder="C"
              onChange={(v) => updateLine(index, 'height_cm', v)}
            />
          </Space.Compact>
        ) : [row.length_cm, row.width_cm, row.height_cm].every((v) => v != null) ? (
          `${row.length_cm} × ${row.width_cm} × ${row.height_cm}`
        ) : (
          '—'
        ),
    },
  ];
  if (editing)
    columns.push({
      title: '',
      width: 46,
      render: (_, __, index) => (
        <Button
          danger
          type="text"
          icon={<DeleteOutlined />}
          aria-label="Xóa dòng"
          disabled={contents.length === 1}
          onClick={() => setContents((items) => items.filter((_, i) => i !== index))}
        />
      ),
    });
  const save = () => {
    onSave({ contents: contents.map(({ line_no, ...line }) => line), cod_amount: codAmount });
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
      <Table
        size="small"
        rowKey={(_, index) => index}
        pagination={false}
        dataSource={contents}
        columns={columns}
      />
      <div className="bill-cod-row">
        <strong>{t('bills.codAmount')}</strong>
        {editing ? (
          <InputNumber
            min={0}
            value={codAmount}
            onChange={(value) => setCodAmount(value || 0)}
            formatter={(v) => `${v}`.replace(/\B(?=(\d{3})+(?!\d))/g, '.')}
            parser={(v) => v.replace(/\./g, '')}
            addonAfter="₫"
          />
        ) : (
          <strong>
            {new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(
              codAmount,
            )}
          </strong>
        )}
      </div>
      {editing && (
        <Space style={{ marginTop: 14 }}>
          <Button
            icon={<PlusOutlined />}
            onClick={() => setContents((items) => [...items, emptyLine()])}
          >
            {t('bills.addLine')}
          </Button>
          <Button type="primary" icon={<SaveOutlined />} loading={saving} onClick={save}>
            {t('common.save')}
          </Button>
          <Button
            onClick={() => {
              setContents(bill.contents.map((line) => ({ ...line })));
              setCodAmount(bill.cod_amount);
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
