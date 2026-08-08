import { createRoot } from 'react-dom/client';
import App from './App';
import './styles/global.css';
import './styles/mobile.css';
import { registerAppSW } from './pwa/registerSW';

createRoot(document.getElementById('root')).render(<App />);

// Register service worker after React mounts
registerAppSW({
  onNeedRefresh: () => {
    // Handled by UpdatePrompt component via the event bus
  },
  onOfflineReady: () => {
    // No-op — online-only app
  },
});
