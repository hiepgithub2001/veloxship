/**
 * Application shell — sidebar + header with Vietnamese menu items.
 */
import { useState } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import { Layout, Menu, Button, Typography, Avatar, Dropdown, Space } from 'antd';
import {
  FileTextOutlined,
  TeamOutlined,
  PlusOutlined,
  LogoutOutlined,
  UserOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
} from '@ant-design/icons';
import { useAuth } from '../../auth/AuthContext';
import { t } from '../../i18n/vi';
import logo from '../../assets/logo.png';

const { Sider, Header, Content } = Layout;
const { Text } = Typography;

export function AppShell() {
  const [collapsed, setCollapsed] = useState(false);
  const { currentUser, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const menuItems = [
    {
      key: '/phieu-gui',
      icon: <FileTextOutlined />,
      label: t('layout.bills'),
    },
    {
      key: '/phieu-gui/tao-moi',
      icon: <PlusOutlined />,
      label: t('layout.createBill'),
    },
    {
      key: '/khach-hang',
      icon: <TeamOutlined />,
      label: t('layout.customers'),
    },
  ];

  const userMenuItems = [
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: t('auth.logout'),
      danger: true,
    },
  ];

  const handleMenuClick = ({ key }) => {
    navigate(key);
  };

  const handleUserMenuClick = ({ key }) => {
    if (key === 'logout') {
      logout();
      navigate('/dang-nhap');
    }
  };

  // Determine which menu item is selected
  const selectedKey = menuItems.find((item) => location.pathname === item.key)?.key
    || menuItems.find((item) => location.pathname.startsWith(item.key) && item.key !== '/phieu-gui/tao-moi')?.key
    || '/phieu-gui';

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider
        collapsible
        collapsed={collapsed}
        onCollapse={setCollapsed}
        trigger={null}
        width={240}
        style={{ position: 'fixed', left: 0, top: 0, bottom: 0, zIndex: 10 }}
      >
        <div
          style={{
            height: 64,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '0 16px',
            borderBottom: '1px solid rgba(255,255,255,0.1)',
          }}
        >
          <img src={logo} alt={t('app.name')} style={{ height: 36 }} />
          {!collapsed && (
            <Text
              strong
              style={{ color: '#fff', marginLeft: 12, fontSize: 16, whiteSpace: 'nowrap' }}
            >
              {t('app.name')}
            </Text>
          )}
        </div>

        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[selectedKey]}
          items={menuItems}
          onClick={handleMenuClick}
          style={{ marginTop: 8 }}
        />
      </Sider>

      <Layout style={{ marginLeft: collapsed ? 80 : 240, transition: 'margin-left 0.2s' }}>
        <Header
          style={{
            background: '#fff',
            padding: '0 24px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            boxShadow: '0 1px 4px rgba(0,0,0,0.08)',
            position: 'sticky',
            top: 0,
            zIndex: 5,
          }}
        >
          <Button
            type="text"
            icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
            onClick={() => setCollapsed(!collapsed)}
          />

          <Dropdown
            menu={{ items: userMenuItems, onClick: handleUserMenuClick }}
            placement="bottomRight"
          >
            <Space style={{ cursor: 'pointer' }}>
              <Avatar icon={<UserOutlined />} style={{ backgroundColor: '#C41E3A' }} />
              <Text strong>{currentUser?.full_name}</Text>
            </Space>
          </Dropdown>
        </Header>

        <Content style={{ margin: 24 }}>
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  );
}

export default AppShell;
