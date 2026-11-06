import { Line } from '@ant-design/plots';

import { buildBillsTrendConfig } from '../chartConfig';

export function BillsTrendChart({ daily }) {
  return <Line {...buildBillsTrendConfig(daily)} />;
}
