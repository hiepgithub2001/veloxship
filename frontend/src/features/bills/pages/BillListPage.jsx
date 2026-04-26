/**
 * Bill list page — placeholder with navigation to create.
 */
import { Button, Card, Empty, Typography } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { t } from '../../../i18n/vi';

const { Title } = Typography;

export function BillListPage() {
  const navigate = useNavigate();

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
        <Title level={3} style={{ margin: 0 }}>{t('bills.title')}</Title>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={() => navigate('/phieu-gui/tao-moi')}
          id="create-bill-btn"
        >
          {t('bills.create')}
        </Button>
      </div>
      <Card>
        <Empty description={t('bills.notFound')} />
      </Card>
    </div>
  );
}

export default BillListPage;
