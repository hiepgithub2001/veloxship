import { PrinterOutlined } from '@ant-design/icons';
import { Alert, Button, Modal, Select, Space, Spin, Typography } from 'antd';
import { useEffect, useRef, useState } from 'react';
import { getBillsPrintHtml } from '../../../api/bills';
import { t } from '../../../i18n/vi';

/**
 * Copy counts the print template can label (mirrors
 * `backend/app/services/print_service.py::_COPY_LABELS`).
 */
export const BILL_COPY_OPTIONS = [1, 2, 3];
const DEFAULT_COPY_COUNT = BILL_COPY_OPTIONS[BILL_COPY_OPTIONS.length - 1];

export function BillBatchPrintModal({ billIds, open, onClose }) {
  const frameRef = useRef(null);
  // Only the first render of a session records a print event; changing the
  // copy count afterwards only refreshes the preview.
  const recordedRef = useRef(false);
  const [copies, setCopies] = useState(DEFAULT_COPY_COUNT);
  const [printHtml, setPrintHtml] = useState(null);
  const [error, setError] = useState(null);

  const idsKey = (billIds || []).join(',');
  const billCount = (billIds || []).length;

  // Opening the modal starts a new print session (and therefore a new record).
  useEffect(() => {
    if (open) recordedRef.current = false;
  }, [open]);

  useEffect(() => {
    if (!open || !billIds || billIds.length === 0) return undefined;

    let active = true;
    const record = !recordedRef.current;
    if (record) recordedRef.current = true;
    setPrintHtml(null);
    setError(null);

    getBillsPrintHtml(billIds, { copies, record })
      .then((html) => {
        if (!active) return;
        setPrintHtml(html);
      })
      .catch((requestError) => {
        if (!active) return;
        // A failed first render did not record anything, so let the next
        // successful render record the print event.
        if (record) recordedRef.current = false;
        setError(requestError);
      });

    return () => {
      active = false;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [idsKey, open, copies]);

  const handleAfterClose = () => {
    recordedRef.current = false;
    setCopies(DEFAULT_COPY_COUNT);
  };

  return (
    <Modal
      className="bill-pdf-modal"
      destroyOnClose
      afterClose={handleAfterClose}
      footer={
        <>
          <Button onClick={onClose}>{t('common.close')}</Button>
          <Button
            type="primary"
            icon={<PrinterOutlined />}
            disabled={!printHtml}
            onClick={() => frameRef.current?.contentWindow?.print()}
          >
            {t('bills.print')}
          </Button>
        </>
      }
      onCancel={onClose}
      open={open}
      title={t('bills.batchPrintTitle')}
      width="min(1100px, 96vw)"
    >
      <div className="bill-batch-print-toolbar">
        <Space size={8} wrap>
          <Typography.Text strong>{t('bills.copyCount')}</Typography.Text>
          <Select
            aria-label={t('bills.copyCount')}
            className="bill-batch-print-copies"
            disabled={!printHtml && !error}
            onChange={setCopies}
            options={BILL_COPY_OPTIONS.map((value) => ({
              label: t('bills.copyCountOption').replace('{count}', String(value)),
              value,
            }))}
            size="small"
            value={copies}
          />
          {billCount > 0 && (
            <Typography.Text type="secondary">
              {t('bills.batchPrintSummary')
                .replace('{bills}', String(billCount))
                .replace('{copies}', String(copies))
                .replace('{pages}', String(billCount * copies))}
            </Typography.Text>
          )}
        </Space>
      </div>
      {!printHtml && !error && (
        <div className="bill-pdf-loading">
          <Spin size="large" />
        </div>
      )}
      {error && (
        <Alert
          message={t('bills.fetchError')}
          description={error.response?.data?.message || 'Vui lòng thử lại.'}
          type="error"
          showIcon
        />
      )}
      {printHtml && (
        <iframe
          ref={frameRef}
          className="bill-pdf-frame"
          srcDoc={printHtml}
          title={t('bills.batchPrintTitle')}
        />
      )}
    </Modal>
  );
}

export default BillBatchPrintModal;
