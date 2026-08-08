/**
 * ConnectionBanner — shows a fixed-top Vietnamese warning when the device goes offline.
 */
import { Alert } from 'antd';
import { WifiOutlined } from '@ant-design/icons';
import { useOnlineStatus } from './useOnlineStatus';

export function ConnectionBanner() {
  const { online } = useOnlineStatus();

  if (online) return null;

  return (
    <div className="pwa-connection-banner" id="connection-banner">
      <Alert
        type="warning"
        showIcon
        icon={<WifiOutlined />}
        message="Mất kết nối — vui lòng kiểm tra mạng và thử lại"
        banner
        closable={false}
      />
    </div>
  );
}

export default ConnectionBanner;
