/**
 * Protected route — redirects to login when not authenticated.
 */
import { Navigate, useLocation } from 'react-router-dom';
import { Spin } from 'antd';
import { useAuth } from './AuthContext';

export function ProtectedRoute({ children }) {
  const { isAuthenticated, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <Spin size="large" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/dang-nhap" state={{ from: location }} replace />;
  }

  return children;
}

export default ProtectedRoute;
