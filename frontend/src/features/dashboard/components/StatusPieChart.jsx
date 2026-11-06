import { Pie } from '@ant-design/plots';

import { buildStatusPieConfig } from '../chartConfig';

export function StatusPieChart({ statusCounts }) {
  return <Pie {...buildStatusPieConfig(statusCounts)} />;
}
