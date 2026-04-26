/**
 * App root — wraps providers.
 */
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { RouterProvider } from 'react-router-dom';
import { AntdConfigProvider } from './styles/theme';
import { AuthProvider } from './auth/AuthContext';
import router from './routes/index';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      staleTime: 30_000,
      refetchOnWindowFocus: false,
    },
  },
});

export function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AntdConfigProvider>
        <AuthProvider>
          <RouterProvider router={router} />
        </AuthProvider>
      </AntdConfigProvider>
    </QueryClientProvider>
  );
}

export default App;
