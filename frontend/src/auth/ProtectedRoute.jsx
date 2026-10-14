/**
 * Protected route — redirects to login when not authenticated.
 */
import { Navigate, useLocation } from 'react-router-dom';
import { Spin } from 'antd';
import { useAuth } from './AuthContext';
import { LOGIN_PATH } from './redirect';

export function ProtectedRoute({ children }) {
  const { isAuthenticated, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return (
      <div
        style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}
      >
        <Spin size="large" />
      </div>
    );
  }

  if (!isAuthenticated) {
    // `from` carries the whole location (path + query + hash) so the login page
    // can send the user back to exactly where the session died.
    return <Navigate to={LOGIN_PATH} state={{ from: location }} replace />;
  }

  return children;
}

export default ProtectedRoute;
