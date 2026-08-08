/**
 * BillCreateMobile — 6-step Vietnamese wizard for creating a bill on mobile.
 * Uses Ant Design <Steps> with per-step validation and error indicators.
 */
import { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { Steps, Button, Card, message, Space } from 'antd';
import {
  ArrowLeftOutlined,
  ArrowRightOutlined,
  SaveOutlined,
  PrinterOutlined,
} from '@ant-design/icons';

import { useBillDraft, BillDraftProvider } from './useBillDraft.jsx';
import { SenderStep, SENDER_FIELDS } from './steps/SenderStep';
import { ReceiverStep, RECEIVER_FIELDS } from './steps/ReceiverStep';
import { ContentsStep, CONTENTS_FIELDS } from './steps/ContentsStep';
import { ServiceStep, SERVICE_FIELDS } from './steps/ServiceStep';
import { FeesStep, FEES_FIELDS } from './steps/FeesStep';
import { ConfirmStep } from './steps/ConfirmStep';
import { createBill } from '../../../api/bills';
import { t } from '../../../i18n/vi';

const STEP_CONFIG = [
  { title: 'Người gửi', fields: SENDER_FIELDS, Component: SenderStep },
  { title: 'Người nhận', fields: RECEIVER_FIELDS, Component: ReceiverStep },
  { title: 'Nội dung', fields: CONTENTS_FIELDS, Component: ContentsStep },
  { title: 'Dịch vụ', fields: SERVICE_FIELDS, Component: ServiceStep },
  { title: 'Cước phí', fields: FEES_FIELDS, Component: FeesStep },
  { title: 'Xác nhận', fields: [], Component: ConfirmStep },
];

export function BillCreateMobile() {
  const methods = useBillDraft();
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState(0);
  const [stepErrors, setStepErrors] = useState({});

  const mutation = useMutation({
    mutationFn: createBill,
    onSuccess: (data) => {
      message.success(t('bills.createSuccess'));
      navigate(`/phieu-gui/tao-moi/preview/${data.id}`);
    },
    onError: (error) => {
      const errorMsg = error.response?.data?.message || 'Lỗi khi tạo phiếu gửi';
      message.error(errorMsg);
    },
  });

  const goToStep = useCallback((step) => {
    setCurrentStep(step);
  }, []);

  const handleNext = useCallback(async () => {
    const step = STEP_CONFIG[currentStep];
    if (step.fields.length > 0) {
      const isValid = await methods.trigger(step.fields);
      if (!isValid) {
        setStepErrors((prev) => ({ ...prev, [currentStep]: true }));
        return;
      }
    }
    setStepErrors((prev) => ({ ...prev, [currentStep]: false }));
    setCurrentStep((prev) => Math.min(prev + 1, STEP_CONFIG.length - 1));
  }, [currentStep, methods]);

  const handlePrev = useCallback(() => {
    setCurrentStep((prev) => Math.max(prev - 1, 0));
  }, []);

  const handleSubmit = useCallback(async () => {
    const isValid = await methods.trigger();
    if (!isValid) {
      // Find first step with errors and navigate there
      for (let i = 0; i < STEP_CONFIG.length - 1; i++) {
        const stepValid = await methods.trigger(STEP_CONFIG[i].fields);
        if (!stepValid) {
          setStepErrors((prev) => ({ ...prev, [i]: true }));
          setCurrentStep(i);
          return;
        }
      }
      return;
    }
    const data = methods.getValues();
    mutation.mutate(data);
  }, [methods, mutation]);

  const stepsItems = STEP_CONFIG.map((step, index) => ({
    title: step.title,
    status: stepErrors[index]
      ? 'error'
      : index < currentStep
        ? 'finish'
        : index === currentStep
          ? 'process'
          : 'wait',
  }));

  const CurrentComponent = STEP_CONFIG[currentStep].Component;
  const isLastStep = currentStep === STEP_CONFIG.length - 1;
  const isFirstStep = currentStep === 0;

  return (
    <BillDraftProvider methods={methods}>
      <div style={{ padding: '0 8px' }}>
        <Steps
          current={currentStep}
          items={stepsItems}
          direction="horizontal"
          size="small"
          className="bill-wizard-steps"
          style={{ marginBottom: 16 }}
          onChange={goToStep}
        />

        <Card
          style={{ marginBottom: 16, minHeight: 300 }}
          styles={{ body: { padding: '16px 12px' } }}
        >
          {isLastStep ? <CurrentComponent goToStep={goToStep} /> : <CurrentComponent />}
        </Card>

        <div style={{ display: 'flex', justifyContent: 'space-between', paddingBottom: 24 }}>
          <Button
            onClick={isFirstStep ? () => navigate('/phieu-gui') : handlePrev}
            icon={<ArrowLeftOutlined />}
            id="mobile-wizard-prev"
          >
            {isFirstStep ? t('common.cancel') : 'Quay lại'}
          </Button>

          {isLastStep ? (
            <Button
              type="primary"
              onClick={handleSubmit}
              loading={mutation.isPending}
              icon={<PrinterOutlined />}
              id="mobile-wizard-submit"
            >
              Lưu & In phiếu
            </Button>
          ) : (
            <Button
              type="primary"
              onClick={handleNext}
              icon={<ArrowRightOutlined />}
              iconPosition="end"
              id="mobile-wizard-next"
            >
              Tiếp tục
            </Button>
          )}
        </div>
      </div>
    </BillDraftProvider>
  );
}

export default BillCreateMobile;
