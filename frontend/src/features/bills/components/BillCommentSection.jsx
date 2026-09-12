import { useState } from 'react';
import { Button, Card, Input } from 'antd';
import { SendOutlined } from '@ant-design/icons';

/**
 * Bill comment section.
 *
 * Placeholder — the comment stream is stubbed here. The composer input is
 * present but not yet wired to an API; it will be implemented in a later iteration.
 */
export function BillCommentSection() {
  const [value, setValue] = useState('');
  return (
    <Card>
      <div className="bill-block-heading">
        <div>
          <h3>Bình luận</h3>
          <span>Trao đổi thông tin về phiếu gửi</span>
        </div>
      </div>
      <div className="bill-comment-composer">
        <Input.TextArea
          value={value}
          onChange={(e) => setValue(e.target.value)}
          placeholder="Viết bình luận..."
          autoSize={{ minRows: 2, maxRows: 6 }}
        />
        <div className="bill-comment-composer-actions">
          <Button type="primary" icon={<SendOutlined />} disabled={!value.trim()}>
            Gửi
          </Button>
        </div>
      </div>
    </Card>
  );
}
export default BillCommentSection;
