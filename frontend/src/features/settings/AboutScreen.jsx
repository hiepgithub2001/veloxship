/**
 * AboutScreen — Settings/About page showing app version and build info.
 */
import { Card, Typography, Divider } from 'antd';
import { InfoCircleOutlined } from '@ant-design/icons';
import { formatVersion, APP_VERSION, APP_GIT_SHA, APP_BUILT_AT } from '../../pwa/version';

const { Title, Text, Paragraph } = Typography;

export function AboutScreen() {
  const buildDate = APP_BUILT_AT
    ? new Date(APP_BUILT_AT).toLocaleString('vi-VN', {
        dateStyle: 'long',
        timeStyle: 'short',
      })
    : '—';

  return (
    <div style={{ maxWidth: 480, margin: '0 auto' }}>
      <Card>
        <div style={{ textAlign: 'center', marginBottom: 16 }}>
          <InfoCircleOutlined style={{ fontSize: 48, color: '#C41E3A', marginBottom: 12 }} />
          <Title level={4} style={{ margin: 0 }}>
            Giới thiệu
          </Title>
        </div>

        <Divider />

        <div style={{ marginBottom: 16 }}>
          <Text type="secondary">Phiên bản</Text>
          <div>
            <Text strong style={{ fontSize: 18 }}>
              v{APP_VERSION}
            </Text>
            <Text type="secondary" style={{ marginLeft: 8 }}>
              ({APP_GIT_SHA})
            </Text>
          </div>
        </div>

        <div style={{ marginBottom: 16 }}>
          <Text type="secondary">Ngày xây dựng</Text>
          <div>
            <Text>{buildDate}</Text>
          </div>
        </div>

        <Divider />

        <Paragraph type="secondary" style={{ fontSize: 13 }}>
          VeloxShip — Ứng dụng quản lý phiếu gửi vận chuyển. Được thiết kế cho nhân viên vận chuyển
          và quầy giao nhận, hỗ trợ tạo phiếu gửi, theo dõi trạng thái, và in phiếu trực tiếp từ
          điện thoại.
        </Paragraph>

        <Text type="secondary" style={{ fontSize: 12 }}>
          {formatVersion()}
        </Text>
      </Card>
    </div>
  );
}

export default AboutScreen;
