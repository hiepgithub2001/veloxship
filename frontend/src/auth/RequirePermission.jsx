/**
 * Permission guards — hide UI the signed-in user is not allowed to use.
 *
 * `<RequirePermission>` wraps a route/page and renders a 403 result when the
 * user lacks the action. `<Can>` is the inline variant for buttons/actions.
 */
import { Button, Result } from 'antd';
import { useNavigate } from 'react-router-dom';
import { homePathFor, usePermission } from './permissions';
import { t } from '../i18n/vi';

/**
 * Resolve the permission predicate for one of the accepted shapes.
 *
 * @returns {{allowed: boolean, can: Function}} the gate result plus the raw
 *   predicate (so callers can compute a fallback route).
 */
function usePermissionGate({ permission, any, all }) {
  const permissions = usePermission();
  const { can, canAny, canAll } = permissions;

  let allowed = true;
  if (permission) allowed = can(permission);
  else if (any) allowed = canAny(any);
  else if (all) allowed = canAll(all);

  return { ...permissions, allowed };
}

/**
 * Route/element guard.
 *
 * @param {object} props
 * @param {string} [props.permission] - required action
 * @param {string[]} [props.any] - require at least one of these actions
 * @param {string[]} [props.all] - require every one of these actions
 */
export function RequirePermission({ permission, any, all, children }) {
  const { allowed, can } = usePermissionGate({ permission, any, all });
  const navigate = useNavigate();

  if (allowed) {
    return children;
  }

  return (
    <Result
      status="403"
      title="403"
      subTitle={t('common.noPermission')}
      extra={
        <Button
          type="primary"
          onClick={() => navigate(homePathFor(can), { replace: true })}
        >
          {t('common.back')}
        </Button>
      }
    />
  );
}

/** Inline guard for buttons/actions — renders nothing when not allowed. */
export function Can({ permission, any, all, children }) {
  const { allowed } = usePermissionGate({ permission, any, all });
  return allowed ? children : null;
}

export default RequirePermission;
