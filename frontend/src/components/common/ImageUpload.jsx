/**
 * ImageUpload — Reusable Ant Design Upload component for single or multi-image upload.
 * Integrates with POST /api/v1/files/upload via uploadFile API.
 */
import { useState, useEffect } from 'react';
import { Upload, Modal, message } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import { uploadFile } from '../../api/files';

/**
 * @param {object} props
 * @param {string[]} [props.value=[]] - Array of image keys or URLs
 * @param {function} props.onChange - Callback when image array changes (newKeys: string[]) => void
 * @param {number} [props.maxCount=5] - Maximum number of images allowed
 * @param {boolean} [props.disabled=false] - Whether upload is disabled
 */
export function ImageUpload({ value = [], onChange, maxCount = 5, disabled = false }) {
  const [fileList, setFileList] = useState([]);
  const [previewOpen, setPreviewOpen] = useState(false);
  const [previewImage, setPreviewImage] = useState('');
  const [previewTitle, setPreviewTitle] = useState('');

  // Sync fileList state with incoming value prop
  useEffect(() => {
    if (Array.isArray(value)) {
      const currentKeys = fileList.map((f) => f.key || f.url || f.response?.key).filter(Boolean);
      const valueKeys = value.filter(Boolean);

      // Only re-sync if the keys array has changed externally
      if (JSON.stringify(currentKeys) !== JSON.stringify(valueKeys)) {
        const syncedList = valueKeys.map((key, index) => ({
          uid: `-${index}`,
          name: key.split('/').pop() || `Image ${index + 1}`,
          status: 'done',
          url: key,
          key: key,
        }));
        setFileList(syncedList);
      }
    } else {
      setFileList([]);
    }
  }, [value]);

  const handlePreview = async (file) => {
    const src = file.url || file.preview || file.thumbUrl;
    setPreviewImage(src);
    setPreviewOpen(true);
    setPreviewTitle(file.name || file.url?.substring(file.url.lastIndexOf('/') + 1));
  };

  const handleCustomRequest = async ({ file, onSuccess, onError, onProgress }) => {
    try {
      const result = await uploadFile(file, {
        onUploadProgress: (event) => {
          const percent = Math.round((event.loaded * 100) / event.total);
          onProgress({ percent });
        },
      });
      onSuccess(result, file);
    } catch (err) {
      message.error(err.response?.data?.message || 'Tải ảnh lên thất bại');
      onError(err);
    }
  };

  const handleFileChange = ({ fileList: newFileList }) => {
    setFileList(newFileList);

    // Extract all successfully uploaded keys/URLs
    const updatedKeys = newFileList
      .filter((f) => f.status === 'done' || f.url)
      .map((f) => f.key || f.url || f.response?.key)
      .filter(Boolean);

    onChange?.(updatedKeys);
  };

  const uploadButton = (
    <div>
      <PlusOutlined />
      <div style={{ marginTop: 8 }}>Tải ảnh lên</div>
    </div>
  );

  return (
    <>
      <Upload
        accept="image/*"
        listType="picture-card"
        fileList={fileList}
        customRequest={handleCustomRequest}
        onPreview={handlePreview}
        onChange={handleFileChange}
        maxCount={maxCount}
        disabled={disabled}
      >
        {fileList.length >= maxCount || disabled ? null : uploadButton}
      </Upload>

      <Modal
        open={previewOpen}
        title={previewTitle}
        footer={null}
        onCancel={() => setPreviewOpen(false)}
      >
        <img alt="Preview" style={{ width: '100%' }} src={previewImage} />
      </Modal>
    </>
  );
}

export default ImageUpload;
