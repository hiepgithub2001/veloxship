/**
 * UpdatePrompt — Vietnamese auto-update affordance.
 * Shows "Có phiên bản mới — tải lại để cập nhật" at bottom-right.
 * Suppressed when the user is mid-wizard on /phieu-gui/tao-moi.
 */
import { useState, useEffect, useCallback } from 'react';
import { useLocation } from 'react-router-dom';
import { Card, Button, Typography, Space } from 'antd';
import { SyncOutlined, CloseOutlined } from '@ant-design/icons';
import { onNeedRefresh, updateSW } from './registerSW';

const { Text } = Typography;

export function UpdatePrompt() {
  const [needsRefresh, setNeedsRefresh] = useState(false);
  const [dismissed, setDismissed] = useState(false);
  const location = useLocation();

  useEffect(() => {
    const unsubscribe = onNeedRefresh(() => {
      setNeedsRefresh(true);
      setDismissed(false);
    });
    return unsubscribe;
  }, []);

  const handleUpdate = useCallback(() => {
    updateSW(true);
  }, []);

  const handleDismiss = useCallback(() => {
    setDismissed(true);
  }, []);

  // Suppress while on the create-bill wizard route
  const isInWizard =
    location.pathname.startsWith('/phieu-gui/tao-moi') && !location.pathname.includes('/preview/');

  if (!needsRefresh || dismissed || isInWizard) return null;

  return (
    <div className="pwa-update-prompt" id="update-prompt">
      <Card
        size="small"
        styles={{ body: { padding: '12px 16px' } }}
        style={{ boxShadow: '0 4px 12px rgba(0,0,0,0.15)', borderRadius: 8 }}
      >
        <div style={{ display: 'flex', alignItems: 'flex-start', gap: 12 }}>
          <SyncOutlined style={{ fontSize: 20, color: '#1890ff', marginTop: 2 }} />
          <div style={{ flex: 1 }}>
            <Text strong style={{ display: 'block', marginBottom: 4 }}>
              Có phiên bản mới
            </Text>
            <Text type="secondary" style={{ fontSize: 13 }}>
              Tải lại để cập nhật ứng dụng
            </Text>
          </div>
          <Button type="text" size="small" icon={<CloseOutlined />} onClick={handleDismiss} />
        </div>
        <Button
          type="primary"
          size="small"
          onClick={handleUpdate}
          style={{ marginTop: 8, width: '100%' }}
          id="update-prompt-accept"
        >
          Cập nhật
        </Button>
      </Card>
    </div>
  );
}

export default UpdatePrompt;
