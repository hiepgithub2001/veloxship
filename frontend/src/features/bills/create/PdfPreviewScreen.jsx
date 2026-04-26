/**
 * PdfPreviewScreen — post-save mobile screen for viewing, downloading, sharing, and printing a bill PDF.
 */
import { useEffect, useRef, useState, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { Button, Spin, Typography, message } from 'antd';
import {
  DownloadOutlined,
  ShareAltOutlined,
  PrinterOutlined,
  ArrowLeftOutlined,
} from '@ant-design/icons';
import client from '../../../api/client';

const { Text } = Typography;

export function PdfPreviewScreen() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [pdfUrl, setPdfUrl] = useState(null);
  const [pdfBlob, setPdfBlob] = useState(null);
  const printIframeRef = useRef(null);

  const { isLoading, error } = useQuery({
    queryKey: ['bill-pdf', id],
    queryFn: async () => {
      const response = await client.get(`/bills/${id}/print?as=pdf`, {
        responseType: 'blob',
      });
      return response.data;
    },
    onSuccess: (blob) => {
      const url = URL.createObjectURL(blob);
      setPdfUrl(url);
      setPdfBlob(blob);
    },
  });

  // Handle the query data manually since onSuccess is deprecated in newer React Query
  const queryResult = useQuery({
    queryKey: ['bill-pdf-data', id],
    queryFn: async () => {
      const response = await client.get(`/bills/${id}/print?as=pdf`, {
        responseType: 'blob',
      });
      return response.data;
    },
    enabled: !pdfBlob,
  });

  useEffect(() => {
    if (queryResult.data && !pdfBlob) {
      const blob = queryResult.data;
      const url = URL.createObjectURL(blob);
      setPdfUrl(url);
      setPdfBlob(blob);
    }
  }, [queryResult.data, pdfBlob]);

  // Cleanup object URL on unmount
  useEffect(() => {
    return () => {
      if (pdfUrl) {
        URL.revokeObjectURL(pdfUrl);
      }
    };
  }, [pdfUrl]);

  const handleDownload = useCallback(() => {
    if (!pdfUrl) return;
    const link = document.createElement('a');
    link.href = pdfUrl;
    link.download = `phieu-gui-${id}.pdf`;
    document.body.appendChild(link);
    link.click();
    link.remove();
  }, [pdfUrl, id]);

  const handleShare = useCallback(async () => {
    if (!pdfBlob) return;

    const file = new File([pdfBlob], `phieu-gui-${id}.pdf`, { type: 'application/pdf' });

    if (navigator.canShare && navigator.canShare({ files: [file] })) {
      try {
        await navigator.share({
          title: `Phiếu gửi ${id}`,
          files: [file],
        });
      } catch (err) {
        if (err.name !== 'AbortError') {
          message.error('Không thể chia sẻ tệp');
        }
      }
    } else {
      message.info('Trình duyệt không hỗ trợ chia sẻ — vui lòng tải xuống');
    }
  }, [pdfBlob, id]);

  const handlePrint = useCallback(() => {
    if (!pdfUrl) return;

    // Create a hidden iframe to load the PDF and trigger print
    const iframe = printIframeRef.current;
    if (iframe) {
      iframe.src = pdfUrl;
      iframe.onload = () => {
        try {
          iframe.contentWindow.print();
        } catch {
          // Cross-origin fallback
          window.open(pdfUrl, '_blank');
        }
      };
    }
  }, [pdfUrl]);

  if (queryResult.isLoading) {
    return (
      <div
        style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '80vh' }}
      >
        <Spin size="large" tip="Đang tải phiếu gửi..." />
      </div>
    );
  }

  if (queryResult.error) {
    return (
      <div style={{ padding: 24, textAlign: 'center' }}>
        <Text type="danger">Không thể tải phiếu gửi</Text>
        <br />
        <Button onClick={() => navigate(-1)} style={{ marginTop: 16 }}>
          Quay lại
        </Button>
      </div>
    );
  }

  return (
    <div className="pdf-preview-container" id="pdf-preview-screen">
      {/* Header */}
      <div
        style={{
          padding: '12px 16px',
          background: '#fff',
          borderBottom: '1px solid #e8e8e8',
          display: 'flex',
          alignItems: 'center',
          gap: 12,
        }}
      >
        <Button
          type="text"
          icon={<ArrowLeftOutlined />}
          onClick={() => navigate('/phieu-gui')}
          id="pdf-preview-back"
        />
        <Text strong style={{ fontSize: 16 }}>
          Phiếu gửi #{id}
        </Text>
      </div>

      {/* PDF iframe */}
      {pdfUrl && (
        <iframe
          src={pdfUrl}
          className="pdf-preview-iframe"
          title="Xem trước phiếu gửi"
          id="pdf-preview-frame"
        />
      )}

      {/* Action buttons */}
      <div className="pdf-preview-actions">
        <Button icon={<DownloadOutlined />} onClick={handleDownload} id="pdf-download-btn">
          Tải xuống
        </Button>
        <Button icon={<ShareAltOutlined />} onClick={handleShare} id="pdf-share-btn">
          Chia sẻ
        </Button>
        <Button icon={<PrinterOutlined />} onClick={handlePrint} id="pdf-print-btn">
          In
        </Button>
      </div>

      {/* Hidden iframe for printing */}
      <iframe ref={printIframeRef} style={{ display: 'none' }} title="In phiếu gửi" />
    </div>
  );
}

export default PdfPreviewScreen;
