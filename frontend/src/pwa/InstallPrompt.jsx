/**
 * InstallPrompt — Vietnamese install banner for Android/Chromium + iOS Safari overlay.
 *
 * Android: Listens for `beforeinstallprompt`, shows a banner with "Cài đặt" / "Để sau".
 * iOS: Detects Safari on iOS, shows instruction overlay for Add to Home Screen.
 *
 * Suppressed when:
 * - Already in standalone mode
 * - Dismissed within last 30 days
 */
import { useState, useEffect, useCallback } from 'react';
import { Alert, Button, Space, Typography } from 'antd';
import {
  DownloadOutlined,
  CloseOutlined,
  ShareAltOutlined,
  PlusSquareOutlined,
} from '@ant-design/icons';

const { Text } = Typography;

const DISMISS_KEY = 'pwa-install-dismissed-at';
const DISMISS_DAYS = 30;

/**
 * Check if the app is running in standalone mode (installed).
 */
function isStandalone() {
  return (
    window.matchMedia('(display-mode: standalone)').matches ||
    // iOS Safari standalone mode
    ('standalone' in navigator && navigator.standalone === true)
  );
}

/**
 * Check if the dismiss window has expired.
 */
function isDismissed() {
  const dismissed = localStorage.getItem(DISMISS_KEY);
  if (!dismissed) return false;
  const elapsed = Date.now() - parseInt(dismissed, 10);
  return elapsed < DISMISS_DAYS * 24 * 60 * 60 * 1000;
}

/**
 * Detect iOS Safari.
 */
function isIOSSafari() {
  const ua = navigator.userAgent;
  const isIOS =
    /iPad|iPhone|iPod/.test(ua) ||
    (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);
  const isSafari = /Safari/.test(ua) && !/CriOS|FxiOS|OPiOS|EdgiOS/.test(ua);
  return isIOS && isSafari;
}

// ===== Android/Chromium Install Banner =====

function AndroidInstallBanner() {
  const [deferredPrompt, setDeferredPrompt] = useState(null);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    if (isStandalone() || isDismissed()) return;

    const handler = (e) => {
      e.preventDefault();
      setDeferredPrompt(e);
      setVisible(true);
    };

    window.addEventListener('beforeinstallprompt', handler);
    return () => window.removeEventListener('beforeinstallprompt', handler);
  }, []);

  const handleInstall = useCallback(async () => {
    if (!deferredPrompt) return;
    deferredPrompt.prompt();
    const { outcome } = await deferredPrompt.userChoice;
    if (outcome === 'accepted') {
      setVisible(false);
    }
    setDeferredPrompt(null);
  }, [deferredPrompt]);

  const handleDismiss = useCallback(() => {
    localStorage.setItem(DISMISS_KEY, String(Date.now()));
    setVisible(false);
  }, []);

  if (!visible) return null;

  return (
    <div className="pwa-install-banner">
      <Alert
        type="info"
        showIcon
        icon={<DownloadOutlined />}
        message="Cài đặt ứng dụng vào màn hình chính"
        description="Truy cập nhanh hơn — không cần mở trình duyệt"
        action={
          <Space direction="vertical" size="small">
            <Button type="primary" size="small" onClick={handleInstall} id="pwa-install-accept">
              Cài đặt
            </Button>
            <Button size="small" onClick={handleDismiss} id="pwa-install-dismiss">
              Để sau
            </Button>
          </Space>
        }
        closable={false}
      />
    </div>
  );
}

// ===== iOS Safari Instruction Overlay =====

function IOSInstallOverlay() {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    if (isStandalone() || isDismissed() || !isIOSSafari()) return;
    setVisible(true);
  }, []);

  const handleDismiss = useCallback(() => {
    localStorage.setItem(DISMISS_KEY, String(Date.now()));
    setVisible(false);
  }, []);

  if (!visible) return null;

  return (
    <div className="pwa-ios-overlay" id="pwa-ios-overlay">
      <div style={{ display: 'flex', alignItems: 'flex-start', gap: 12 }}>
        <div style={{ flex: 1 }}>
          <Text strong style={{ fontSize: 15, display: 'block', marginBottom: 8 }}>
            Cài đặt ứng dụng
          </Text>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
            <Text>1. Bấm</Text>
            <ShareAltOutlined style={{ fontSize: 18, color: '#1890ff' }} />
            <Text strong>Chia sẻ</Text>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <Text>2. Chọn</Text>
            <PlusSquareOutlined style={{ fontSize: 18, color: '#1890ff' }} />
            <Text strong>Thêm vào Màn hình chính</Text>
          </div>
        </div>
        <Button
          type="text"
          icon={<CloseOutlined />}
          onClick={handleDismiss}
          size="small"
          id="pwa-ios-dismiss"
        />
      </div>
    </div>
  );
}

// ===== Main Component =====

export function InstallPrompt() {
  // Don't render anything if already standalone
  if (typeof window !== 'undefined' && isStandalone()) return null;

  return (
    <>
      <AndroidInstallBanner />
      <IOSInstallOverlay />
    </>
  );
}

export default InstallPrompt;
