/**
 * Application routes — Vietnamese URL paths.
 */
import { createBrowserRouter, Navigate } from 'react-router-dom';
import { ProtectedRoute } from '../auth/ProtectedRoute';
import { AppShell } from '../components/layout/AppShell';
import { LoginPage } from '../features/auth/pages/LoginPage';
import { BillListPage } from '../features/bills/pages/BillListPage';
import { BillCreatePage } from '../features/bills/pages/BillCreatePage';
import { BillDetailPage } from '../features/bills/pages/BillDetailPage';

// Placeholder for customers (later phase)
function PlaceholderPage({ title }) {
  return (
    <div style={{ padding: 24, textAlign: 'center', color: '#999' }}>
      <h2>{title}</h2>
      <p>Đang phát triển...</p>
    </div>
  );
}

const router = createBrowserRouter([
  {
    path: '/dang-nhap',
    element: <LoginPage />,
  },
  {
    path: '/',
    element: (
      <ProtectedRoute>
        <AppShell />
      </ProtectedRoute>
    ),
    children: [
      {
        index: true,
        element: <Navigate to="/phieu-gui" replace />,
      },
      {
        path: 'phieu-gui',
        element: <BillListPage />,
      },
      {
        path: 'phieu-gui/tao-moi',
        element: <BillCreatePage />,
      },
      {
        path: 'phieu-gui/:id',
        element: <BillDetailPage />,
      },
      {
        path: 'khach-hang',
        element: <PlaceholderPage title="Danh sách khách hàng" />,
      },
    ],
  },
]);

export default router;
