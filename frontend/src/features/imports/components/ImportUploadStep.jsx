/**
 * Step 1 of the Excel import wizard — pick the .xlsx file and show the layout
 * the parser accepts.
 *
 * The checks here are only a UX pre-check (extension + size). The backend
 * re-validates the file and reports row-level problems for the preview step.
 */
import { DeleteOutlined, FileExcelOutlined, InboxOutlined } from '@ant-design/icons';
import { Alert, Button, Card, Input, Space, Tag, Typography, Upload, message } from 'antd';

import { t } from '../../../i18n/vi';

/** Mirrors the backend upload limit (`IMPORT_FILE_MAX_SIZE`). */
const MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024;

/** Human-readable file size for the selected-file line. */
function formatFileSize(bytes) {
  if (bytes >= 1024 * 1024) return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
  return `${Math.max(1, Math.round(bytes / 1024))} KB`;
}

const isXlsxFile = (file) => file.name.toLowerCase().endsWith('.xlsx');

export function ImportUploadStep({
  file,
  onFileChange,
  sender,
  onSenderChange,
  disabled = false,
}) {
  const handleBeforeUpload = (candidate) => {
    if (!isXlsxFile(candidate)) {
      message.error(t('imports.errors.invalidType'));
      return Upload.LIST_IGNORE;
    }
    if (candidate.size > MAX_FILE_SIZE_BYTES) {
      message.error(t('imports.errors.fileTooLarge'));
      return Upload.LIST_IGNORE;
    }

    onFileChange(candidate);
    // Never let antd upload: the wizard posts the file itself together with options.
    return false;
  };

  const layoutColumns = t('imports.upload.layoutColumns');

  return (
    <div className="import-upload-step">
      <Upload.Dragger
        accept=".xlsx"
        beforeUpload={handleBeforeUpload}
        disabled={disabled}
        fileList={[]}
        maxCount={1}
        multiple={false}
        showUploadList={false}
      >
        <p className="ant-upload-drag-icon">
          <InboxOutlined />
        </p>
        <p className="ant-upload-text">{t('imports.upload.draggerTitle')}</p>
        <p className="ant-upload-hint">{t('imports.upload.draggerHint')}</p>
      </Upload.Dragger>

      {file && (
        <Alert
          type="info"
          showIcon
          icon={<FileExcelOutlined />}
          message={file.name}
          description={formatFileSize(file.size)}
          action={
            <Button
              size="small"
              icon={<DeleteOutlined />}
              disabled={disabled}
              onClick={() => onFileChange(null)}
            >
              {t('imports.upload.removeFile')}
            </Button>
          }
        />
      )}

      <Card size="small" title={t('imports.upload.senderTitle')}>
        <Typography.Paragraph type="secondary" className="import-upload-sender-hint">
          {t('imports.upload.senderHint')}
        </Typography.Paragraph>
        <Space size={16} wrap className="import-upload-sender">
          <label className="import-upload-sender-field">
            <Typography.Text type="secondary" className="import-upload-sender-label">
              {t('imports.upload.senderName')}
            </Typography.Text>
            <Input
              allowClear
              disabled={disabled}
              maxLength={120}
              placeholder={t('imports.upload.senderNamePlaceholder')}
              value={sender?.name || ''}
              onChange={(event) => onSenderChange?.({ ...sender, name: event.target.value })}
            />
          </label>
          <label className="import-upload-sender-field">
            <Typography.Text type="secondary" className="import-upload-sender-label">
              {t('imports.upload.senderPhone')}
            </Typography.Text>
            <Input
              allowClear
              disabled={disabled}
              maxLength={20}
              placeholder={t('imports.upload.senderPhonePlaceholder')}
              value={sender?.phone || ''}
              onChange={(event) => onSenderChange?.({ ...sender, phone: event.target.value })}
            />
          </label>
        </Space>
      </Card>

      <Card size="small" title={t('imports.upload.layoutTitle')}>
        <Typography.Paragraph type="secondary" className="import-upload-layout-hint">
          {t('imports.upload.layoutHint')}
        </Typography.Paragraph>
        <Space size={[8, 8]} wrap>
          {layoutColumns.map((column) => (
            <Tag key={column}>{column}</Tag>
          ))}
        </Space>
        <Alert
          className="import-upload-layout-note"
          type="warning"
          showIcon
          message={t('imports.upload.layoutNote')}
        />
      </Card>
    </div>
  );
}

export default ImportUploadStep;
