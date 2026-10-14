/**
 * Vietnamese login page.
 *
 * Also the landing spot for an expired session: when the refresh token is
 * rejected the provider flags `sessionExpired`, which is surfaced here as a
 * notice, and `location.state.from` sends the user back to the page they were
 * on once they sign in again.
 */
import { useEffect, useState } from 'react';
import { useNavigate, useLocation, Navigate } from 'react-router-dom';
import { Alert, Button, Card, Form, Input, message, Typography } from 'antd';
import { LockOutlined, UserOutlined } from '@ant-design/icons';
import { useAuth } from '../../../auth/AuthContext';
import { can, homePathFor } from '../../../auth/permissions';
import { resolveReturnPath } from '../../../auth/redirect';
import { t } from '../../../i18n/vi';
import logo from '../../../assets/logo.png';

const { Title, Text } = Typography;

export function LoginPage() {
  const [loading, setLoading] = useState(false);
  const [showExpiredNotice, setShowExpiredNotice] = useState(false);
  const {
    login,
    currentUser,
    isAuthenticated,
    loading: restoring,
    sessionExpired,
    clearSessionExpired,
  } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  // Surface the "session expired" notice once, then clear the flag so a later
  // manual visit to this page does not repeat it.
  useEffect(() => {
    if (sessionExpired) {
      setShowExpiredNotice(true);
      clearSessionExpired();
    }
  }, [sessionExpired, clearSessionExpired]);

  // A signed-in user has no business on the login page.
  if (!restoring && isAuthenticated) {
    return <Navigate to={homePathFor((action) => can(currentUser, action))} replace />;
  }

  const handleSubmit = async (values) => {
    setLoading(true);
    try {
      const user = await login(values.username, values.password);
      // Fall back to the first page this role may actually open, so a user
      // without `bill:view` is not dropped on a 403.
      const fallback = homePathFor((action) => can(user, action));
      navigate(resolveReturnPath(location.state?.from, fallback), { replace: true });
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
        padding: 16,
        background: 'linear-gradient(135deg, #1A1A1A 0%, #2D1A1F 50%, #1A1A1A 100%)',
      }}
    >
      <Card
        style={{
          width: '100%',
          maxWidth: 400,
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

        {showExpiredNotice && (
          <Alert
            type="warning"
            showIcon
            message={t('auth.sessionExpired')}
            style={{ marginBottom: 16 }}
            id="login-session-expired"
            closable
            onClose={() => setShowExpiredNotice(false)}
          />
        )}

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
