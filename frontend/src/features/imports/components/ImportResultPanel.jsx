/**
 * Step 3 of the Excel import wizard — commit summary.
 *
 * The contract's `ImportSummary` carries row counters only, so the "new
 * customers" statistic is rendered defensively: if the backend adds a
 * `customers_created` counter (top-level or in `summary`) it shows up here,
 * otherwise the card is simply omitted.
 */
import { Alert, Button, Card, Col, Row, Space, Statistic, Tag, Typography, message } from 'antd';
import { DownloadOutlined, UnorderedListOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';

import { downloadImportResult } from '../../../api/imports';
import { t } from '../../../i18n/vi';
import { IMPORT_BATCH_STATUS_COLORS, importBatchStatusLabel } from '../importStatus';

export function ImportResultPanel({ batch, onClose }) {
  const navigate = useNavigate();

  const status = batch?.status;
  const summary = batch?.summary ?? {};
  const importedRows = summary.imported_rows ?? 0;
  const warningRows = summary.warning_rows ?? 0;
  const errorRows = summary.error_rows ?? 0;
  const customersCreated = summary.customers_created ?? batch?.customers_created;

  const downloadMutation = useMutation({
    mutationFn: () => downloadImportResult(batch.id),
    onError: (error) => {
      message.error(error.response?.data?.message || t('imports.errors.downloadError'));
    },
  });

  const handleViewBills = () => {
    onClose?.();
    navigate('/phieu-gui');
  };

  let banner;
  if (status === 'failed') {
    banner = {
      type: 'error',
      title: t('imports.result.failed'),
      description: batch?.error_message || null,
    };
  } else if (status === 'partially_completed') {
    banner = {
      type: 'warning',
      title: t('imports.result.partiallyCompleted')
        .replace('{count}', importedRows)
        .replace('{skipped}', errorRows),
      description: null,
    };
  } else if (status === 'completed') {
    banner = {
      type: 'success',
      title: t('imports.result.completed').replace('{count}', importedRows),
      description: null,
    };
  } else {
    banner = { type: 'info', title: t('imports.result.pending'), description: null };
  }

  return (
    <div className="import-result-panel">
      <Alert
        type={banner.type}
        showIcon
        message={banner.title}
        description={banner.description}
        action={
          <Tag color={IMPORT_BATCH_STATUS_COLORS[status] || 'default'}>
            {importBatchStatusLabel(status)}
          </Tag>
        }
      />

      <Row gutter={[12, 12]}>
        <Col xs={24} sm={12} md={8}>
          <Card size="small">
            <Statistic title={t('imports.result.billsCreated')} value={importedRows} />
          </Card>
        </Col>
        {typeof customersCreated === 'number' && (
          <Col xs={24} sm={12} md={8}>
            <Card size="small">
              <Statistic title={t('imports.result.customersCreated')} value={customersCreated} />
            </Card>
          </Col>
        )}
        <Col xs={24} sm={12} md={8}>
          <Card size="small">
            <Statistic title={t('imports.result.warningRows')} value={warningRows} />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={8}>
          <Card size="small">
            <Statistic title={t('imports.result.errorRows')} value={errorRows} />
          </Card>
        </Col>
      </Row>

      <Space direction="vertical" size={8}>
        <Space wrap>
          <Button
            type="primary"
            icon={<DownloadOutlined />}
            loading={downloadMutation.isPending}
            onClick={() => downloadMutation.mutate()}
          >
            {t('imports.result.downloadResult')}
          </Button>
          <Button icon={<UnorderedListOutlined />} onClick={handleViewBills}>
            {t('imports.result.viewBills')}
          </Button>
        </Space>
        <Typography.Text type="secondary">{t('imports.result.downloadResultHint')}</Typography.Text>
      </Space>
    </div>
  );
}

export default ImportResultPanel;
