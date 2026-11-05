/**
 * Step 2 of the Excel import wizard — preview the validated rows.
 *
 * The batch response carries at most 200 preview rows; filtering therefore runs
 * client-side on that slice and the table tells the user when the preview was
 * truncated (more rows exist in the result workbook).
 */
import { useMemo, useState } from 'react';
import { Alert, Button, Flex, Segmented, Space, Table, Tag, Tooltip, Typography, message } from 'antd';
import { DownloadOutlined } from '@ant-design/icons';
import { useMutation } from '@tanstack/react-query';

import { downloadImportResult } from '../../../api/imports';
import { formatWeight } from '../../../lib/format';
import { t } from '../../../i18n/vi';
import { IMPORT_ROW_STATUS_COLORS, importRowStatusLabel } from '../importStatus';

/** Rows returned in `ImportBatchRead.preview` (backend cap). */
const PREVIEW_LIMIT = 200;

/** Convert a weight that may arrive as a decimal string ("43.500") into a number. */
function toWeight(value) {
  if (value == null || value === '') return null;
  const number = Number(value);
  return Number.isFinite(number) ? number : null;
}

/**
 * Province cell: show "old → new" only when the import remapped the province,
 * otherwise just the resolved province name.
 */
function ProvinceCell({ row }) {
  const data = row.normalized_data ?? {};
  const raw = (data.destination_raw || '').trim();
  const province = (data.province_name || '').trim();

  if (!province) return <Typography.Text type="secondary">{raw || '—'}</Typography.Text>;
  if (!raw || raw === province) return <span>{province}</span>;

  return (
    <Space size={4} wrap={false}>
      <Typography.Text type="secondary">{raw}</Typography.Text>
      <Typography.Text type="secondary">→</Typography.Text>
      <Typography.Text strong>{province}</Typography.Text>
    </Space>
  );
}

/** Issues cell: the error message first, then each warning for the row. */
function IssuesCell({ row }) {
  const issues = [];
  if (row.error_message) {
    issues.push(
      <Typography.Text key="error" type="danger">
        {row.error_message}
      </Typography.Text>
    );
  }
  (row.warnings || []).forEach((warning, index) => {
    issues.push(
      <Typography.Text key={`warning-${index}`} type="warning">
        {warning}
      </Typography.Text>
    );
  });

  if (issues.length === 0) return <Typography.Text type="secondary">—</Typography.Text>;
  return <div className="import-issues">{issues}</div>;
}

export function ImportPreviewTable({ batch }) {
  const [statusFilter, setStatusFilter] = useState('all');

  const previewRows = useMemo(() => batch?.preview ?? [], [batch]);

  const counts = useMemo(
    () =>
      previewRows.reduce(
        (acc, row) => {
          acc.all += 1;
          if (row.status && acc[row.status] !== undefined) acc[row.status] += 1;
          return acc;
        },
        { all: 0, ok: 0, warning: 0, error: 0 }
      ),
    [previewRows]
  );

  const filteredRows = useMemo(
    () =>
      statusFilter === 'all'
        ? previewRows
        : previewRows.filter((row) => row.status === statusFilter),
    [previewRows, statusFilter]
  );

  const downloadMutation = useMutation({
    mutationFn: () => downloadImportResult(batch.id),
    onError: (error) => {
      // A blob request returns a Blob on error, so `message` is usually undefined.
      message.error(error.response?.data?.message || t('imports.errors.downloadError'));
    },
  });

  const summary = batch?.summary ?? {};
  const totalRows = summary.total_rows ?? 0;
  const okRows = summary.ok_rows ?? 0;
  const warningRows = summary.warning_rows ?? 0;
  const errorRows = summary.error_rows ?? 0;

  const summaryText = t('imports.preview.summary')
    .replace('{total}', totalRows)
    .replace('{ok}', okRows)
    .replace('{warning}', warningRows)
    .replace('{error}', errorRows);

  const summaryNotes = [];
  if (errorRows > 0) {
    summaryNotes.push(t('imports.preview.errorsPresent').replace('{count}', errorRows));
  }
  if (warningRows > 0) {
    summaryNotes.push(t('imports.preview.warningsPresent').replace('{count}', warningRows));
  }

  const filterOptions = [
    { value: 'all', label: `${t('imports.preview.filterAll')} (${counts.all})` },
    { value: 'ok', label: `${t('imports.preview.filterOk')} (${counts.ok})` },
    { value: 'warning', label: `${t('imports.preview.filterWarning')} (${counts.warning})` },
    { value: 'error', label: `${t('imports.preview.filterError')} (${counts.error})` },
  ];

  const columns = [
    {
      title: t('imports.columns.rowNumber'),
      dataIndex: 'row_number',
      key: 'row_number',
      width: 100,
      align: 'center',
    },
    {
      title: t('imports.columns.trackingNumber'),
      key: 'tracking_number',
      width: 150,
      render: (_, row) => (
        <Typography.Text strong>{row.normalized_data?.tracking_number || '—'}</Typography.Text>
      ),
    },
    {
      title: t('imports.columns.sender'),
      key: 'sender_name',
      width: 180,
      render: (_, row) => {
        const name = row.normalized_data?.sender_name;
        const phone = row.normalized_data?.sender_phone;
        if (!name && !phone) {
          return (
            <Typography.Text type="secondary">
              {t('imports.columns.defaultSender')}
            </Typography.Text>
          );
        }
        return (
          <div className="import-preview-sender">
            <Typography.Text>{name || '—'}</Typography.Text>
            {phone ? (
              <Typography.Text type="secondary">{phone}</Typography.Text>
            ) : null}
          </div>
        );
      },
    },
    {
      title: t('imports.columns.receiverName'),
      key: 'receiver_name',
      width: 180,
      ellipsis: true,
      render: (_, row) => row.normalized_data?.receiver_name || '—',
    },
    {
      title: t('imports.columns.province'),
      key: 'province',
      width: 200,
      render: (_, row) => <ProvinceCell row={row} />,
    },
    {
      title: t('imports.columns.phone'),
      key: 'phone',
      width: 140,
      render: (_, row) => row.normalized_data?.contact_phone || '—',
    },
    {
      title: t('imports.columns.packages'),
      key: 'packages',
      width: 100,
      align: 'right',
      render: (_, row) => row.normalized_data?.packages ?? '—',
    },
    {
      title: t('imports.columns.weight'),
      key: 'weight',
      width: 130,
      align: 'right',
      render: (_, row) => {
        const weight = toWeight(row.normalized_data?.weight_kg);
        return weight == null ? '—' : formatWeight(weight);
      },
    },
    {
      title: t('imports.columns.status'),
      dataIndex: 'status',
      key: 'status',
      width: 120,
      render: (status) => (
        <Tag color={IMPORT_ROW_STATUS_COLORS[status] || 'default'}>
          {importRowStatusLabel(status)}
        </Tag>
      ),
    },
    {
      title: t('imports.columns.issues'),
      key: 'issues',
      width: 340,
      render: (_, row) => <IssuesCell row={row} />,
    },
  ];

  return (
    <div>
      <Alert
        className="import-preview-summary"
        type={errorRows > 0 ? 'warning' : warningRows > 0 ? 'info' : 'success'}
        showIcon
        message={summaryText}
        description={
          summaryNotes.length > 0 ? (
            <ul className="import-preview-summary-list">
              {summaryNotes.map((note) => (
                <li key={note}>{note}</li>
              ))}
            </ul>
          ) : null
        }
      />

      {totalRows > PREVIEW_LIMIT && (
        <Alert
          className="import-preview-summary"
          type="info"
          showIcon
          message={t('imports.preview.truncated')}
        />
      )}

      {(batch?.warnings || []).length > 0 && (
        <Alert
          className="import-preview-summary"
          type="warning"
          showIcon
          message={t('imports.preview.fileWarnings')}
          description={
            <ul className="import-preview-summary-list">
              {batch.warnings.map((warning) => (
                <li key={warning}>{warning}</li>
              ))}
            </ul>
          }
        />
      )}

      <Flex className="import-preview-toolbar" justify="space-between" align="center" gap={12} wrap>
        <Space wrap>
          <Typography.Text type="secondary">{t('imports.preview.filterLabel')}</Typography.Text>
          <Segmented options={filterOptions} value={statusFilter} onChange={setStatusFilter} />
        </Space>
        <Tooltip title={t('imports.preview.downloadErrorFileHint')}>
          <Button
            icon={<DownloadOutlined />}
            loading={downloadMutation.isPending}
            onClick={() => downloadMutation.mutate()}
          >
            {t('imports.preview.downloadErrorFile')}
          </Button>
        </Tooltip>
      </Flex>

      <Table
        columns={columns}
        dataSource={filteredRows}
        locale={{ emptyText: t('imports.preview.noRowsInFilter') }}
        pagination={{
          pageSize: 20,
          showSizeChanger: true,
          pageSizeOptions: [10, 20, 50, 100],
          showTotal: (total) => t('imports.preview.showingRows').replace('{count}', total),
        }}
        rowKey={(row) => row.id ?? row.row_number}
        scroll={{ x: 'max-content' }}
        size="small"
      />
    </div>
  );
}

export default ImportPreviewTable;
