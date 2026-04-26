/**
 * Bill creation page — composes all bill form components.
 */
import { useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm, useFieldArray, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useMutation } from '@tanstack/react-query';
import { Button, Card, message, Space, Divider, Typography } from 'antd';
import { SaveOutlined, PrinterOutlined } from '@ant-design/icons';
import { useReactToPrint } from 'react-to-print';

import { billCreateSchema } from '../schema';
import { createBill } from '../../../api/bills';
import { SenderBlock } from '../components/SenderBlock';
import { ReceiverBlock } from '../components/ReceiverBlock';
import { ContentTable } from '../components/ContentTable';
import { ServiceTierSelector } from '../components/ServiceTierSelector';
import { FeeBreakdownInput } from '../components/FeeBreakdownInput';
import { BillPrintView } from '../components/BillPrintView';
import { t } from '../../../i18n/vi';

const { Title } = Typography;

const defaultValues = {
  customer_id: null,
  customer_code: null,
  sender: { name: '', address: '', district: '', province: '', phone: '' },
  receiver: { name: '', address: '', district: '', province: '', phone: '' },
  contents: [{ description: '', quantity: 1, weight_kg: 0, length_cm: null, width_cm: null, height_cm: null }],
  cargo_type: 'goods',
  service_tier_code: '',
  fee: { fee_main: 0, fee_fuel_surcharge: 0, fee_other_surcharge: 0, fee_vat: 0, fee_total: 0 },
  payer: 'sender',
};

export function BillCreatePage() {
  const navigate = useNavigate();
  const printRef = useRef(null);
  const [createdBill, setCreatedBill] = useState(null);

  const {
    control,
    handleSubmit,
    watch,
    setValue,
    formState: { errors },
  } = useForm({
    resolver: zodResolver(billCreateSchema),
    defaultValues,
  });

  const { fields, append, remove } = useFieldArray({
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

  const handlePrint = useReactToPrint({
    contentRef: printRef,
  });

  const onSubmit = (data) => {
    mutation.mutate(data);
  };

  // After bill is created, show print view
  if (createdBill) {
    return (
      <div>
        <Space style={{ marginBottom: 16 }}>
          <Button
            type="primary"
            icon={<PrinterOutlined />}
            onClick={handlePrint}
            id="print-bill"
          >
            {t('bills.print')}
          </Button>
          <Button onClick={() => navigate(`/phieu-gui/${createdBill.id}`)}>
            {t('bills.detail')}
          </Button>
          <Button onClick={() => { setCreatedBill(null); }}>
            {t('bills.create')}
          </Button>
        </Space>

        <div ref={printRef}>
          <BillPrintView bill={createdBill} />
        </div>
      </div>
    );
  }

  return (
    <div>
      <Title level={3} style={{ marginBottom: 24 }}>
        {t('bills.create')}
      </Title>

      <form onSubmit={handleSubmit(onSubmit)}>
        <div style={{ display: 'flex', gap: 16, marginBottom: 16 }}>
          <Card style={{ flex: 1 }}>
            <SenderBlock control={control} errors={errors} />
          </Card>
          <Card style={{ flex: 1 }}>
            <ReceiverBlock control={control} errors={errors} />
          </Card>
        </div>

        <Card style={{ marginBottom: 16 }}>
          <ContentTable
            fields={fields}
            append={append}
            remove={remove}
            setValue={setValue}
            watch={watch}
          />
          {errors?.contents && (
            <div style={{ color: '#ff4d4f', marginTop: 8 }}>{errors.contents.message || errors.contents.root?.message}</div>
          )}
        </Card>

        <div style={{ display: 'flex', gap: 16, marginBottom: 16 }}>
          <Card style={{ flex: 1 }}>
            <ServiceTierSelector
              cargoType={watch('cargo_type')}
              tierCode={watch('service_tier_code')}
              onCargoTypeChange={(val) => {
                setValue('cargo_type', val);
                setValue('service_tier_code', '');
              }}
              onTierChange={(code) => setValue('service_tier_code', code)}
            />
            {errors?.cargo_type && (
              <div style={{ color: '#ff4d4f' }}>{errors.cargo_type.message}</div>
            )}
            {errors?.service_tier_code && (
              <div style={{ color: '#ff4d4f' }}>{errors.service_tier_code.message}</div>
            )}
          </Card>
          <Card style={{ flex: 1 }}>
            <FeeBreakdownInput watch={watch} setValue={setValue} errors={errors} />
          </Card>
        </div>

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
