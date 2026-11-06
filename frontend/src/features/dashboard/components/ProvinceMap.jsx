import { ComposableMap, Geographies, Geography } from 'react-simple-maps';

import vietnamTopology from '../../../assets/geo/vietnam-provinces.json';
import { provinceCountById, scaleProvinceColor } from '../chartConfig';

/**
 * Vietnam choropleth (react-simple-maps). Colours each province by its bill
 * count; hover is styled via `.dashboard-map .rsm-geography:hover` in global CSS.
 * Hover/click report the province code up to the parent panel.
 */
export function ProvinceMap({ destinations, onHover, onSelect }) {
  const counts = provinceCountById(destinations);
  const max = Math.max(0, ...Object.values(counts));

  return (
    <div className="dashboard-map">
      <ComposableMap
        projection="geoMercator"
        projectionConfig={{ center: [106.7, 16.4], scale: 2400 }}
        style={{ width: '100%', height: '100%' }}
      >
        <Geographies geography={vietnamTopology}>
          {({ geographies }) =>
            geographies.map((geo) => {
              const code = geo.properties?.code;
              const count = counts[code] ?? 0;
              return (
                <Geography
                  key={geo.rsmKey}
                  geography={geo}
                  fill={scaleProvinceColor(count, max)}
                  stroke="#FFFFFF"
                  strokeWidth={0.6}
                  tabIndex={-1}
                  onMouseEnter={() => onHover?.(code)}
                  onMouseLeave={() => onHover?.(null)}
                  onClick={() => onSelect?.(code)}
                />
              );
            })
          }
        </Geographies>
      </ComposableMap>
    </div>
  );
}
