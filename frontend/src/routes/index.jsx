/**
 * Application routes — Vietnamese URL paths.
 *
 * Every business route is wrapped in `<RequirePermission>` so a user without
 * the matching action sees a 403 result instead of the page. The backend
 * enforces the same actions, so this is a UX gate only.
 */
import { createBrowserRouter, Navigate } from 'react-router-dom';
import { ProtectedRoute } from '../auth/ProtectedRoute';
import { RequirePermission } from '../auth/RequirePermission';
import { homePathFor, usePermission } from '../auth/permissions';
import { AppShell } from '../components/layout/AppShell';
import { LoginPage } from '../features/auth/pages/LoginPage';
import { BillListPage } from '../features/bills/pages/BillListPage';
import { BillCreatePage } from '../features/bills/pages/BillCreatePage';
import { BillDetailPage } from '../features/bills/pages/BillDetailPage';
import { DepotListPage } from '../features/depots/pages/DepotListPage';
import { VehicleListPage } from '../features/vehicles/pages/VehicleListPage';
import { CustomerListPage } from '../features/customers/pages/CustomerListPage';
import { StaffPage } from '../features/staff/pages/StaffPage';
import { PermissionPage } from '../features/permissions/pages/PermissionPage';
import { AccountPage } from '../features/account/pages/AccountPage';

/** Send the user to the first page their role may open (never a guaranteed 403). */
function HomeRedirect() {
  const { can } = usePermission();
  return <Navigate to={homePathFor(can)} replace />;
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
        element: <HomeRedirect />,
      },
      {
        path: 'phieu-gui',
        element: (
          <RequirePermission permission="bill:view">
            <BillListPage />
          </RequirePermission>
        ),
      },
      {
        path: 'phieu-gui/tao-moi',
        element: (
          <RequirePermission permission="bill:create">
            <BillCreatePage />
          </RequirePermission>
        ),
      },
      {
        path: 'phieu-gui/:id',
        element: (
          <RequirePermission permission="bill:view">
            <BillDetailPage />
          </RequirePermission>
        ),
      },
      {
        path: 'khach-hang',
        element: (
          <RequirePermission permission="customer:view">
            <CustomerListPage />
          </RequirePermission>
        ),
      },
      {
        path: 'buu-cuc',
        element: (
          <RequirePermission permission="depot:view">
            <DepotListPage />
          </RequirePermission>
        ),
      },
      {
        path: 'doi-xe',
        element: (
          <RequirePermission permission="fleet:view">
            <VehicleListPage />
          </RequirePermission>
        ),
      },
      {
        path: 'nhan-vien',
        element: (
          <RequirePermission permission="iam:view_users">
            <StaffPage />
          </RequirePermission>
        ),
      },
      {
        path: 'phan-quyen',
        element: (
          <RequirePermission permission="iam:manage_permissions">
            <PermissionPage />
          </RequirePermission>
        ),
      },
      {
        path: 'tai-khoan',
        element: <AccountPage />,
      },
    ],
  },
]);

export default router;
