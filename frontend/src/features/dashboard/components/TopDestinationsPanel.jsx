import { useState } from 'react';
import { Bar } from '@ant-design/plots';
import { Card, Col, Empty, Row, Typography } from 'antd';

import { t } from '../../../i18n/vi';
import { buildTopDestinationsBarConfig } from '../chartConfig';
import { ProvinceMap } from './ProvinceMap';

/**
 * Top destination panel: a Vietnam choropleth (left) plus a horizontal bar chart
 * of the top provinces (right) — two columns on large screens, stacked on
 * mobile. Hovering/clicking a province on the map highlights the matching bar
 * and shows its name + count in the caption.
 */
export function TopDestinationsPanel({ destinations }) {
  const [selectedCode, setSelectedCode] = useState(null);
  const [hoverCode, setHoverCode] = useState(null);

  const rows = destinations || [];
  const byCode = Object.fromEntries(rows.map((d) => [d.province_code, d]));
  const activeCode = hoverCode ?? selectedCode;
  const active = byCode[activeCode];
  const hasData = rows.some((d) => d.count > 0);

  return (
    <Card
      className="dashboard-chart-card"
      title={<Typography.Text strong>{t('dashboard.chartDestinations')}</Typography.Text>}
    >
      {!hasData ? (
        <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description={t('dashboard.empty')} />
      ) : (
        <Row gutter={[16, 16]}>
          <Col xs={24} lg={14}>
            <ProvinceMap
              destinations={rows}
              onHover={setHoverCode}
              onSelect={setSelectedCode}
            />
            <div className="dashboard-map-caption">
              {active
                ? `${active.province_name} — ${active.count} ${t('dashboard.unitBills')}`
                : t('dashboard.mapHint')}
            </div>
          </Col>
          <Col xs={24} lg={10}>
            <div
              className="dashboard-chart"
              role="img"
              aria-label={t('dashboard.chartDestinationsBar')}
            >
              <Bar {...buildTopDestinationsBarConfig(rows, { selectedCode: activeCode })} />
            </div>
          </Col>
        </Row>
      )}
    </Card>
  );
}
