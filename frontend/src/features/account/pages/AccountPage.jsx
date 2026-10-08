/**
 * AccountPage — Quản lý tài khoản hiện tại (hồ sơ + đổi mật khẩu).
 * Người dùng có thể cập nhật ảnh đại diện, thông tin cá nhân và đổi mật khẩu.
 */
import { useState } from 'react';
import {
  Avatar,
  Button,
  Card,
  Col,
  Descriptions,
  Form,
  Input,
  Row,
  Typography,
  Upload,
  message,
} from 'antd';
import { CameraOutlined, LockOutlined, UserOutlined } from '@ant-design/icons';

import { useAuth } from '../../../auth/AuthContext';
import { changePassword, updateMe } from '../../../api/auth';
import { uploadFile } from '../../../api/files';
import { t } from '../../../i18n/vi';

const { Title, Text } = Typography;

const ROLE_LABELS = {
  admin: 'Quản trị viên',
  operator: 'Nhân viên quầy',
  depot_manager: 'Thủ kho',
  cashier: 'Thủ quỹ',
  accountant: 'Kế toán',
  shipper: 'Bưu tá',
};

export function AccountPage() {
  const { currentUser, refreshMe } = useAuth();
  const [profileForm] = Form.useForm();
  const [passwordForm] = Form.useForm();
  const [savingProfile, setSavingProfile] = useState(false);
  const [savingPassword, setSavingPassword] = useState(false);
  const [uploadingAvatar, setUploadingAvatar] = useState(false);

  const handleSaveProfile = async (values) => {
    setSavingProfile(true);
    try {
      await updateMe({ full_name: values.full_name, phone: values.phone || null });
      await refreshMe();
      message.success(t('account.profileSaved'));
    } catch (err) {
      message.error(err.response?.data?.message || t('account.profileError'));
    } finally {
      setSavingProfile(false);
    }
  };

  const handleChangePassword = async (values) => {
    setSavingPassword(true);
    try {
      await changePassword({
        current_password: values.current_password,
        new_password: values.new_password,
      });
      message.success(t('account.passwordChanged'));
      passwordForm.resetFields();
    } catch (err) {
      message.error(err.response?.data?.message || t('account.passwordError'));
    } finally {
      setSavingPassword(false);
    }
  };

  const handleAvatarUpload = async ({ file, onSuccess, onError }) => {
    setUploadingAvatar(true);
    try {
      const result = await uploadFile(file);
      await updateMe({ avatar: result.key });
      await refreshMe();
      message.success(t('account.avatarUpdated'));
      onSuccess?.(result, file);
    } catch (err) {
      message.error(err.response?.data?.message || t('account.avatarError'));
      onError?.(err);
    } finally {
      setUploadingAvatar(false);
    }
  };

  return (
    <div>
      <Title level={3} style={{ marginTop: 0 }}>
        {t('account.title')}
      </Title>

      <Row gutter={[16, 16]}>
        <Col xs={24} lg={10}>
          <Card style={{ textAlign: 'center' }}>
            <Upload
              accept="image/*"
              showUploadList={false}
              customRequest={handleAvatarUpload}
              disabled={uploadingAvatar}
            >
              <div style={{ position: 'relative', display: 'inline-block', cursor: 'pointer' }}>
                <Avatar
                  size={112}
                  src={currentUser?.avatar || undefined}
                  icon={<UserOutlined />}
                  style={{ backgroundColor: 'var(--color-primary)' }}
                />
                <div
                  style={{
                    position: 'absolute',
                    right: 0,
                    bottom: 0,
                    width: 32,
                    height: 32,
                    borderRadius: '50%',
                    background: '#fff',
                    boxShadow: '0 2px 8px rgba(0,0,0,0.18)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}
                >
                  <CameraOutlined style={{ color: 'var(--color-primary)' }} />
                </div>
              </div>
            </Upload>

            <div style={{ marginTop: 12 }}>
              <Text strong style={{ fontSize: 18, display: 'block' }}>
                {currentUser?.full_name}
              </Text>
              <Text type="secondary">{uploadingAvatar ? t('account.uploading') : t('account.avatarHint')}</Text>
            </div>

            <Descriptions column={1} size="small" style={{ marginTop: 24, textAlign: 'left' }}>
              <Descriptions.Item label={t('account.username')}>
                {currentUser?.username}
              </Descriptions.Item>
              <Descriptions.Item label={t('account.role')}>
                {ROLE_LABELS[currentUser?.role] || currentUser?.role}
              </Descriptions.Item>
              {currentUser?.department && (
                <Descriptions.Item label={t('account.department')}>
                  {currentUser.department}
                </Descriptions.Item>
              )}
              {currentUser?.position && (
                <Descriptions.Item label={t('account.position')}>
                  {currentUser.position}
                </Descriptions.Item>
              )}
              {currentUser?.employee_code && (
                <Descriptions.Item label={t('account.employeeCode')}>
                  {currentUser.employee_code}
                </Descriptions.Item>
              )}
            </Descriptions>
          </Card>
        </Col>

        <Col xs={24} lg={14}>
          <Card title={t('account.profileTitle')} style={{ marginBottom: 16 }}>
            <Form
              form={profileForm}
              layout="vertical"
              onFinish={handleSaveProfile}
              initialValues={{
                full_name: currentUser?.full_name,
                phone: currentUser?.phone,
              }}
            >
              <Form.Item
                name="full_name"
                label={t('account.fullName')}
                rules={[{ required: true, message: t('validation.required') }]}
              >
                <Input placeholder={t('account.fullNamePlaceholder')} />
              </Form.Item>

              <Form.Item
                name="phone"
                label={t('account.phone')}
                rules={[
                  {
                    pattern: /^0\d{9}$/,
                    message: t('validation.invalidPhone'),
                  },
                ]}
              >
                <Input placeholder={t('account.phonePlaceholder')} />
              </Form.Item>

              <Button type="primary" htmlType="submit" loading={savingProfile}>
                {t('common.save')}
              </Button>
            </Form>
          </Card>

          <Card title={t('account.passwordTitle')}>
            <Form form={passwordForm} layout="vertical" onFinish={handleChangePassword}>
              <Form.Item
                name="current_password"
                label={t('account.currentPassword')}
                rules={[{ required: true, message: t('validation.required') }]}
              >
                <Input.Password prefix={<LockOutlined />} autoComplete="current-password" />
              </Form.Item>

              <Form.Item
                name="new_password"
                label={t('account.newPassword')}
                rules={[
                  { required: true, message: t('validation.required') },
                  { min: 6, message: t('account.passwordMin') },
                ]}
              >
                <Input.Password prefix={<LockOutlined />} autoComplete="new-password" />
              </Form.Item>

              <Form.Item
                name="confirm_password"
                label={t('account.confirmPassword')}
                dependencies={['new_password']}
                rules={[
                  { required: true, message: t('validation.required') },
                  ({ getFieldValue }) => ({
                    validator(_, value) {
                      if (!value || getFieldValue('new_password') === value) {
                        return Promise.resolve();
                      }
                      return Promise.reject(new Error(t('account.passwordMismatch')));
                    },
                  }),
                ]}
              >
                <Input.Password prefix={<LockOutlined />} autoComplete="new-password" />
              </Form.Item>

              <Button type="primary" htmlType="submit" loading={savingPassword}>
                {t('account.changePassword')}
              </Button>
            </Form>
          </Card>
        </Col>
      </Row>
    </div>
  );
}

export default AccountPage;
