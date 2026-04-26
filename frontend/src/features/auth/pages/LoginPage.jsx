/**
 * Vietnamese login page.
 */
import { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Button, Card, Form, Input, message, Typography } from 'antd';
import { LockOutlined, UserOutlined } from '@ant-design/icons';
import { useAuth } from '../../../auth/AuthContext';
import { t } from '../../../i18n/vi';
import logo from '../../../assets/logo.png';

const { Title, Text } = Typography;

export function LoginPage() {
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const from = location.state?.from?.pathname || '/phieu-gui';

  const handleSubmit = async (values) => {
    setLoading(true);
    try {
      await login(values.username, values.password);
      navigate(from, { replace: true });
    } catch {
      message.error(t('auth.loginFailed'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'linear-gradient(135deg, #1A1A1A 0%, #2D1A1F 50%, #1A1A1A 100%)',
      }}
    >
      <Card
        style={{
          width: 400,
          borderRadius: 12,
          boxShadow: '0 8px 32px rgba(0,0,0,0.3)',
        }}
      >
        <div style={{ textAlign: 'center', marginBottom: 32 }}>
          <img src={logo} alt={t('app.name')} style={{ height: 64, marginBottom: 16 }} />
          <Title level={3} style={{ margin: 0 }}>
            {t('app.name')}
          </Title>
          <Text type="secondary">{t('app.tagline')}</Text>
        </div>

        <Form layout="vertical" onFinish={handleSubmit} autoComplete="off">
          <Form.Item
            name="username"
            rules={[{ required: true, message: t('validation.required') }]}
          >
            <Input
              prefix={<UserOutlined />}
              placeholder={t('auth.username')}
              size="large"
              id="login-username"
            />
          </Form.Item>

          <Form.Item
            name="password"
            rules={[{ required: true, message: t('validation.required') }]}
          >
            <Input.Password
              prefix={<LockOutlined />}
              placeholder={t('auth.password')}
              size="large"
              id="login-password"
            />
          </Form.Item>

          <Form.Item>
            <Button
              type="primary"
              htmlType="submit"
              block
              size="large"
              loading={loading}
              id="login-submit"
            >
              {t('auth.loginButton')}
            </Button>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
}

export default LoginPage;
