import { Column } from '@ant-design/plots';

import { buildRevenueTrendConfig } from '../chartConfig';

export function RevenueTrendChart({ daily }) {
  return <Column {...buildRevenueTrendConfig(daily)} />;
}
