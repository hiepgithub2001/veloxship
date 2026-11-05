/**
 * ImportWizard — 3-step modal that turns an Excel file into bills.
 *
 *   1. Pick & upload the .xlsx (server validates, nothing is written yet)
 *   2. Preview the validated rows and confirm
 *   3. Show the commit result
 *
 * The batch/file state lives here and is reset whenever the modal opens or
 * closes, so a stale batch can never leak into the next import. Every mutation
 * captures a `runId`; a response that lands after a reset is ignored.
 */
import { useCallback, useEffect, useRef, useState } from 'react';
import { Button, Modal, Steps, Typography, message } from 'antd';
import { useMutation } from '@tanstack/react-query';

import { commitImport, importErrorMessage, validateImport } from '../../../api/imports';
import { t } from '../../../i18n/vi';
import { ImportPreviewTable } from './ImportPreviewTable';
import { ImportResultPanel } from './ImportResultPanel';
import { ImportUploadStep } from './ImportUploadStep';

const STEP_UPLOAD = 0;
const STEP_PREVIEW = 1;
const STEP_RESULT = 2;

/** Statuses after which the bill list is stale and worth refetching. */
const COMMITTED_STATUSES = ['completed', 'partially_completed'];

export function ImportWizard({ open, onClose, onCompleted }) {
  const [step, setStep] = useState(STEP_UPLOAD);
  const [file, setFile] = useState(null);
  const [sender, setSender] = useState({ name: '', phone: '' });
  const [batch, setBatch] = useState(null);
  const runIdRef = useRef(0);

  /**
   * Return to a clean slate. Bumping `runId` also makes any in-flight response
   * from the previous session a no-op.
   */
  const resetWizard = useCallback(() => {
    runIdRef.current += 1;
    setStep(STEP_UPLOAD);
    setFile(null);
    setSender({ name: '', phone: '' });
    setBatch(null);
  }, []);

  // Reset on open (defensive) and after the close animation, so the closing
  // modal still shows its current step while the next session starts clean.
  useEffect(() => {
    if (open) resetWizard();
  }, [open, resetWizard]);

  /**
   * Sender override for files without a "Người gửi" column. Empty values are
   * omitted so the backend falls back to the company default.
   */
  const buildOptions = useCallback(() => {
    const options = {};
    if (sender.name.trim()) options.sender_name = sender.name.trim();
    if (sender.phone.trim()) options.sender_phone = sender.phone.trim();
    return Object.keys(options).length > 0 ? options : undefined;
  }, [sender]);

  const validateMutation = useMutation({
    mutationFn: async (selectedFile) => {
      const runId = runIdRef.current;
      try {
        const data = await validateImport(selectedFile, buildOptions());
        return { runId, data };
      } catch (error) {
        return { runId, error };
      }
    },
    onSuccess: ({ runId, data, error }) => {
      if (runId !== runIdRef.current) return;
      if (error) {
        message.error(importErrorMessage(error, t('imports.errors.uploadError')));
        return;
      }
      setBatch(data);
      setStep(STEP_PREVIEW);
    },
  });

  const commitMutation = useMutation({
    mutationFn: async (batchId) => {
      const runId = runIdRef.current;
      try {
        const data = await commitImport(batchId, { skipErrorRows: true });
        return { runId, data };
      } catch (error) {
        return { runId, error };
      }
    },
    onSuccess: ({ runId, data, error }) => {
      if (runId !== runIdRef.current) return;
      if (error) {
        message.error(importErrorMessage(error, t('imports.errors.commitError')));
        return;
      }
      setBatch(data);
      setStep(STEP_RESULT);
      if (COMMITTED_STATUSES.includes(data?.status)) {
        onCompleted?.(data);
      }
    },
  });

  const handleClose = () => onClose?.();

  const handleValidate = () => {
    if (!file) {
      message.warning(t('imports.errors.fileRequired'));
      return;
    }
    validateMutation.mutate(file);
  };

  const handleCommit = () => {
    if (!batch) return;
    commitMutation.mutate(batch.id);
  };

  const hasValidRows = (batch?.summary?.ok_rows ?? 0) + (batch?.summary?.warning_rows ?? 0) > 0;

  const stepItems = [
    { title: t('imports.steps.upload'), description: t('imports.stepDescription.upload') },
    { title: t('imports.steps.preview'), description: t('imports.stepDescription.preview') },
    { title: t('imports.steps.result'), description: t('imports.stepDescription.result') },
  ];

  const renderFooter = () => {
    if (step === STEP_UPLOAD) {
      return [
        <Button key="cancel" onClick={handleClose}>
          {t('common.cancel')}
        </Button>,
        <Button
          key="validate"
          type="primary"
          disabled={!file || validateMutation.isPending}
          loading={validateMutation.isPending}
          onClick={handleValidate}
        >
          {validateMutation.isPending ? t('imports.upload.uploading') : t('imports.upload.start')}
        </Button>,
      ];
    }

    if (step === STEP_PREVIEW) {
      return [
        <Button
          key="back"
          disabled={commitMutation.isPending}
          onClick={() => setStep(STEP_UPLOAD)}
        >
          {t('imports.preview.backToUpload')}
        </Button>,
        <Button
          key="commit"
          type="primary"
          disabled={!hasValidRows || commitMutation.isPending}
          loading={commitMutation.isPending}
          onClick={handleCommit}
        >
          {commitMutation.isPending ? t('imports.preview.committing') : t('imports.preview.confirm')}
        </Button>,
      ];
    }

    return [
      <Button key="close" type="primary" onClick={handleClose}>
        {t('common.close')}
      </Button>,
    ];
  };

  return (
    <Modal
      afterClose={resetWizard}
      className="import-wizard-modal"
      footer={renderFooter()}
      maskClosable={false}
      onCancel={handleClose}
      open={open}
      title={t('imports.title')}
      width="min(1100px, 96vw)"
    >
      <Typography.Paragraph type="secondary">{t('imports.description')}</Typography.Paragraph>
      <Steps className="import-wizard-steps" current={step} items={stepItems} size="small" />
      <div className="import-wizard-body">
        {step === STEP_UPLOAD && (
          <ImportUploadStep
            disabled={validateMutation.isPending}
            file={file}
            onFileChange={setFile}
            sender={sender}
            onSenderChange={setSender}
          />
        )}
        {step === STEP_PREVIEW && batch && <ImportPreviewTable batch={batch} />}
        {step === STEP_RESULT && batch && (
          <ImportResultPanel batch={batch} onClose={handleClose} />
        )}
      </div>
    </Modal>
  );
}

export default ImportWizard;
