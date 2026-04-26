/**
 * CompatNotice — once-per-session Vietnamese banner for browsers that don't support PWA.
 * Feature-detects serviceWorker + isSecureContext.
 */
import { useState, useEffect } from 'react';
import { Alert } from 'antd';

const SESSION_KEY = 'pwa-compat-notice-shown';

/**
 * Check if the browser supports PWA installation.
 * Exported for testability.
 */
export function isPWASupported() {
  return 'serviceWorker' in navigator && window.isSecureContext;
}

export function CompatNotice() {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    if (isPWASupported()) return;
    if (sessionStorage.getItem(SESSION_KEY)) return;

    setVisible(true);
    sessionStorage.setItem(SESSION_KEY, '1');
  }, []);

  if (!visible) return null;

  return (
    <Alert
      type="info"
      message="Trình duyệt không hỗ trợ cài đặt — phiên bản web vẫn hoạt động bình thường"
      closable
      onClose={() => setVisible(false)}
      style={{ margin: '8px 16px' }}
      id="compat-notice"
    />
  );
}

export default CompatNotice;
