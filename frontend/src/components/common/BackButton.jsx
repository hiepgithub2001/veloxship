/**
 * BackButton — shared "go back" button.
 *
 * Uses browser history (`navigate(-1)`) so the user returns to the exact page
 * they came from — preserving filters, pagination, etc. Falls back to `fallback`
 * when there is no in-app history (e.g. the page was opened directly via a link).
 */
import { Button } from 'antd';
import { ArrowLeftOutlined } from '@ant-design/icons';
import { useLocation, useNavigate } from 'react-router-dom';
import { t } from '../../i18n/vi';

/**
 * @param {object} props
 * @param {string} [props.fallback] - Route to go to when there is no previous page.
 * @param {React.ReactNode} [props.children] - Custom label (defaults to t('common.back')).
 */
export default function BackButton({ fallback = '/phieu-gui', children, ...rest }) {
  const navigate = useNavigate();
  const location = useLocation();

  const handleClick = () => {
    if (location.key === 'default') {
      navigate(fallback, { replace: true });
    } else {
      navigate(-1);
    }
  };

  return (
    <Button icon={<ArrowLeftOutlined />} onClick={handleClick} {...rest}>
      {children ?? t('common.back')}
    </Button>
  );
}
