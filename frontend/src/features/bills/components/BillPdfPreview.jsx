import { PrinterOutlined } from '@ant-design/icons';
import { Alert, Button, Modal, Spin } from 'antd';
import { useEffect, useRef, useState } from 'react';
import { getBillPrintHtml } from '../../../api/bills';
import './BillPdfPreview.css';

export function BillPdfPreview({ billId, open, onClose }) {
  const frameRef = useRef(null);
  const [printHtml, setPrintHtml] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!open || !billId) return undefined;

    let active = true;
    setPrintHtml(null);
    setError(null);

    getBillPrintHtml(billId)
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
  }, [billId, open]);

  return (
    <Modal
      className="bill-pdf-modal"
      destroyOnClose
      footer={
        <>
          <Button onClick={onClose}>Đóng</Button>
          <Button
            type="primary"
            icon={<PrinterOutlined />}
            disabled={!printHtml}
            onClick={() => frameRef.current?.contentWindow?.print()}
          >
            In phiếu
          </Button>
        </>
      }
      onCancel={onClose}
      open={open}
      title="Xem trước phiếu gửi PDF"
      width="min(1100px, 96vw)"
    >
      {!printHtml && !error && (
        <div className="bill-pdf-loading">
          <Spin size="large" />
        </div>
      )}
      {error && (
        <Alert
          message="Không thể tải phiếu PDF"
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
          title="Phiếu gửi PDF"
        />
      )}
    </Modal>
  );
}

export default BillPdfPreview;
