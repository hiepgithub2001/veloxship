/**
 * Bill creation page — composes all bill form components (UC-WEB-19).
 */
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm, useFieldArray } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useMutation } from '@tanstack/react-query';
import { Button, Card, message, Space, Divider, Typography } from 'antd';
import { SaveOutlined, PrinterOutlined } from '@ant-design/icons';

import { billCreateSchema } from '../schema';
import { createBill } from '../../../api/bills';
import { SenderBlock } from '../components/SenderBlock';
import { ReceiverBlock } from '../components/ReceiverBlock';
import { ContentTable } from '../components/ContentTable';
import { FeeBreakdownInput } from '../components/FeeBreakdownInput';
import { BillPdfPreview } from '../components/BillPdfPreview';
import { t } from '../../../i18n/vi';

const { Title } = Typography;

const emptyParty = {
  customer_id: null,
  name: '',
  phone: '',
  address_detail: '',
  province_code: '',
  province_name: '',
  ward_code: '',
  ward_name: '',
};

const defaultValues = {
  sender: { ...emptyParty },
  receiver: { ...emptyParty },
  contents: [
    {
      cargo_type: 'goods',
      description: '',
      quantity: 1,
      weight_kg: 0,
      length_cm: null,
      width_cm: null,
      height_cm: null,
      images: [],
      metadata: {},
    },
  ],
  note: '',
  fee: { fee_main: 0, fee_insurance: 0, fee_other: 0, fee_vat: 0, fee_total: 0 },
  payer: 'sender',
};

export function BillCreatePage() {
  const navigate = useNavigate();
  const [createdBill, setCreatedBill] = useState(null);
  const [pdfOpen, setPdfOpen] = useState(false);

  const {
    control,
    handleSubmit,
    watch,
    setValue,
    getValues,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(billCreateSchema),
    defaultValues,
  });

  const { fields, append, remove, move, insert } = useFieldArray({
    control,
    name: 'contents',
  });

  const mutation = useMutation({
    mutationFn: createBill,
    onSuccess: (data) => {
      message.success(t('bills.createSuccess'));
      setCreatedBill(data);
    },
    onError: (error) => {
      const errorMsg = error.response?.data?.message || t('common.loading');
      message.error(errorMsg);
    },
  });

  const handlePrint = () => setPdfOpen(true);

  const onSubmit = (data) => {
    mutation.mutate(data);
  };

  // After bill is created, show print view
  if (createdBill) {
    return (
      <div>
        <Space style={{ marginBottom: 16 }}>
          <Button type="primary" icon={<PrinterOutlined />} onClick={handlePrint} id="print-bill">
            {t('bills.print')}
          </Button>
          <Button onClick={() => navigate(`/phieu-gui/${createdBill.id}`)}>
            {t('bills.detail')}
          </Button>
          <Button
            onClick={() => {
              setCreatedBill(null);
            }}
          >
            {t('bills.create')}
          </Button>
        </Space>

        <Card>
          <Title level={3} style={{ margin: 0 }}>
            {createdBill.tracking_number}
          </Title>
          <div style={{ marginTop: 8 }}>Phiếu gửi đã sẵn sàng để in dưới dạng PDF A5.</div>
        </Card>
        <BillPdfPreview billId={createdBill.id} open={pdfOpen} onClose={() => setPdfOpen(false)} />
      </div>
    );
  }

  return (
    <div>
      <Title level={3} style={{ marginBottom: 24 }}>
        {t('bills.create')}
      </Title>

      <form onSubmit={handleSubmit(onSubmit)}>
        <div className="bill-party-pair">
          <Card>
            <SenderBlock control={control} errors={errors} setValue={setValue} watch={watch} />
          </Card>
          <Card>
            <ReceiverBlock control={control} errors={errors} setValue={setValue} watch={watch} />
          </Card>
        </div>

        <Card style={{ marginBottom: 16 }}>
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
          {errors?.contents && (
            <div style={{ color: '#ff4d4f', marginTop: 8 }}>
              {errors.contents.message || errors.contents.root?.message}
            </div>
          )}
        </Card>

        <Card style={{ marginBottom: 16 }}>
          <FeeBreakdownInput watch={watch} setValue={setValue} errors={errors} />
        </Card>

        <Divider />

        <Space>
          <Button
            type="primary"
            htmlType="submit"
            icon={<SaveOutlined />}
            loading={mutation.isPending}
            size="large"
            id="save-and-print"
          >
            {t('bills.saveAndPrint')}
          </Button>
          <Button onClick={() => navigate('/phieu-gui')} size="large">
            {t('common.cancel')}
          </Button>
        </Space>
      </form>
    </div>
  );
}

export default BillCreatePage;
