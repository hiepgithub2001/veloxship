# Vietnam provinces map data

`vietnam-provinces.json` is a simplified TopoJSON of Vietnam's 34 post-2025
administrative provinces, used by the dashboard choropleth.

- **Source:** [adminvsrm/GISData](https://github.com/adminvsrm/GISData) —
  `Vietnam Administrative Divisions (Post-2025) / Provinces.geojson`.
- **License:** free for public use with attribution requested (see the source
  repository README — "Copyright and Attribution").
- **Attribution:** Nguyen Duy Liem. (2025). *Vietnam GIS Data*. GitHub.
  https://github.com/nguyenduy1133/Free-GIS-Data

## Preprocessing (one-time)

1. Download `Provinces.geojson` (34 features).
2. Fix a source defect: the Mekong-delta polygon for **Đồng Tháp** is
   mislabeled `Lạng Sơn` (the real Lạng Sơn sits far north). The corrupted
   feature is detected by its centroid latitude and renamed `Đồng Tháp`.
3. Normalize each feature name and annotate `properties.code` with the
   `provinces.open-api.vn` province code used by the backend (`1`, `4`, … `96`).
4. Simplify and convert:
   `npx mapshaper -i vn_clean.geojson -simplify 4% keep-shapes -o format=topojson vietnam-provinces.json`

The frontend joins the dashboard `destinations[].province_code` against
`feature.properties.code`.
