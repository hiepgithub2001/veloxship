/**
 * App root — wraps providers and mounts PWA components globally.
 */
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { RouterProvider } from 'react-router-dom';
import { AntdConfigProvider } from './styles/theme';
import { AuthProvider } from './auth/AuthContext';
import { InstallPrompt } from './pwa/InstallPrompt';
import { ConnectionBanner } from './pwa/ConnectionBanner';
import { CompatNotice } from './pwa/CompatNotice';
import router from './routes/index';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      staleTime: 30_000,
      refetchOnWindowFocus: false,
      networkMode: 'online',
    },
    mutations: {
      networkMode: 'online',
    },
  },
});

export function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AntdConfigProvider>
        <AuthProvider>
          {/* PWA: Connection loss banner — fixed top, highest z-index */}
          <ConnectionBanner />
          {/* PWA: Browser compatibility notice */}
          <CompatNotice />
          {/* Main app router */}
          <RouterProvider router={router} />
          {/* PWA: Install prompt — fixed bottom */}
          <InstallPrompt />
        </AuthProvider>
      </AntdConfigProvider>
    </QueryClientProvider>
  );
}

export default App;
