import { PrinterOutlined } from '@ant-design/icons';
import { Alert, Button, Modal, Spin } from 'antd';
import { useEffect, useRef, useState } from 'react';
import { getBillsPrintHtml } from '../../../api/bills';
import { t } from '../../../i18n/vi';

export function BillBatchPrintModal({ billIds, open, onClose }) {
  const frameRef = useRef(null);
  const [printHtml, setPrintHtml] = useState(null);
  const [error, setError] = useState(null);

  const idsKey = (billIds || []).join(',');

  useEffect(() => {
    if (!open || !billIds || billIds.length === 0) return undefined;

    let active = true;
    setPrintHtml(null);
    setError(null);

    getBillsPrintHtml(billIds)
      .then((html) => {
        if (!active) return;
        setPrintHtml(html);
      })
      .catch((requestError) => {
        if (active) setError(requestError);
      });

    return () => {
      active = false;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [idsKey, open]);

  return (
    <Modal
      className="bill-pdf-modal"
      destroyOnClose
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
