/**
 * NoConnectionScreen — full-screen Vietnamese message when the app launches while offline.
 * Shows "Cần kết nối mạng để sử dụng ứng dụng" with a retry button.
 */
import { Button, Typography } from 'antd';
import { WifiOutlined, ReloadOutlined } from '@ant-design/icons';

const { Title, Paragraph } = Typography;

export function NoConnectionScreen() {
  return (
    <div className="pwa-no-connection" id="no-connection-screen">
      <WifiOutlined style={{ fontSize: 64, color: '#d9d9d9', marginBottom: 24 }} />
      <Title level={3}>Cần kết nối mạng để sử dụng ứng dụng</Title>
      <Paragraph type="secondary">
        Vui lòng kiểm tra kết nối Wi-Fi hoặc dữ liệu di động và thử lại.
      </Paragraph>
      <Button
        type="primary"
        icon={<ReloadOutlined />}
        size="large"
        onClick={() => window.location.reload()}
        id="retry-connection"
      >
        Thử lại
      </Button>
    </div>
  );
}

export default NoConnectionScreen;
