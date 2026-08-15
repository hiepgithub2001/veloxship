/**
 * ImagePreviewGroup — Reusable component for rendering thumbnail image gallery with preview in tables.
 */
import { Image, Space } from 'antd';

/**
 * @param {object} props
 * @param {string[]} [props.images] - Array of image URLs/keys
 * @param {number} [props.width=40] - Thumbnail width
 * @param {number} [props.height=40] - Thumbnail height
 */
export function ImagePreviewGroup({ images, width = 40, height = 40 }) {
  if (!images || images.length === 0) return '—';

  return (
    <Image.PreviewGroup>
      <Space size={4}>
        <Image
          width={width}
          height={height}
          style={{ objectFit: 'cover', borderRadius: 4 }}
          src={images[0]}
          alt="thumbnail"
        />
        {images.length > 1 && (
          <span style={{ fontSize: 12, color: '#8c8c8c' }}>
            +{images.length - 1}
          </span>
        )}
        {images.slice(1).map((url, idx) => (
          <Image key={idx} src={url} style={{ display: 'none' }} />
        ))}
      </Space>
    </Image.PreviewGroup>
  );
}

export default ImagePreviewGroup;
