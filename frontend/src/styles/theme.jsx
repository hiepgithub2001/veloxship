/**
 * Ant Design theme configuration with brand colors from the carrier logo.
 */
import { ConfigProvider } from 'antd';
import viVN from 'antd/locale/vi_VN';

// Brand colors extracted from the logo (red/black tones)
const brandColors = {
  primary: '#C41E3A',      // Rich carrier red
  primaryHover: '#A01830',
  primaryActive: '#8B1528',
  info: '#1890FF',
  success: '#52C41A',
  warning: '#FAAD14',
  error: '#FF4D4F',
  textBase: '#1A1A1A',
  bgBase: '#FAFAFA',
};

const theme = {
  token: {
    colorPrimary: brandColors.primary,
    colorInfo: brandColors.info,
    colorSuccess: brandColors.success,
    colorWarning: brandColors.warning,
    colorError: brandColors.error,
    colorTextBase: brandColors.textBase,
    colorBgBase: brandColors.bgBase,
    borderRadius: 6,
    fontFamily:
      "'Be Vietnam Pro', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
  },
  components: {
    Button: {
      colorPrimary: brandColors.primary,
      colorPrimaryHover: brandColors.primaryHover,
      colorPrimaryActive: brandColors.primaryActive,
    },
    Layout: {
      siderBg: '#1A1A1A',
      headerBg: '#FFFFFF',
      bodyBg: '#F5F5F5',
    },
    Menu: {
      darkItemBg: '#1A1A1A',
      darkItemSelectedBg: brandColors.primary,
    },
  },
};

/**
 * Ant Design ConfigProvider wrapper with Vietnamese locale and brand theme.
 */
export function AntdConfigProvider({ children }) {
  return (
    <ConfigProvider locale={viVN} theme={theme}>
      {children}
    </ConfigProvider>
  );
}

export { brandColors, theme };
export default AntdConfigProvider;
