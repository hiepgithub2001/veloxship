/**
 * CommentSection — Reusable comment thread attached to a polymorphic entity.
 *
 * Renders a composer + root comments with one level of inline replies. Author
 * can edit / soft-delete their own comments; admin can modify anyone's.
 * Images are embedded inline in the rich text (TipTap), not a separate gallery.
 */
import { useState } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { Avatar, Button, Card, Empty, Popconfirm, Space, Spin, Typography, message } from 'antd';
import { DeleteOutlined, EditOutlined, SendOutlined } from '@ant-design/icons';
import { createComment, deleteComment, listComments, updateComment } from '../../api/comments';
import { uploadFile } from '../../api/files';
import { useAuth } from '../../auth/AuthContext';
import { formatViDateTime } from '../../lib/format';
import { t } from '../../i18n/vi';
import { RichText } from './RichText';
import { RichTextEditor } from './RichTextEditor';

const { Text } = Typography;

/** Upload an image and resolve to a displayable URL for the TipTap editor. */
async function uploadCommentImage(file) {
  const result = await uploadFile(file);
  if (!result?.url) throw new Error('Tải ảnh lên thất bại');
  return result.url;
}

function Composer({ value, onChange, onSubmit, submitting, placeholder }) {
  return (
    <div className="comment-composer">
      <RichTextEditor
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        disabled={submitting}
        onUploadImage={uploadCommentImage}
      />
      <div className="comment-composer-actions">
        <Button
          type="primary"
          icon={<SendOutlined />}
          loading={submitting}
          disabled={!value.trim()}
          onClick={onSubmit}
        >
          {t('comments.send')}
        </Button>
      </div>
    </div>
  );
}

function CommentItem({ comment, entityType, entityId, currentUser, queryKey }) {
  const qc = useQueryClient();
  const [replying, setReplying] = useState(false);
  const [replyBody, setReplyBody] = useState('');
  const [editing, setEditing] = useState(false);
  const [editBody, setEditBody] = useState(comment.body);

  const canModify =
    currentUser && (currentUser.id === comment.author_id || currentUser.role === 'admin');

  const reply = useMutation({
    mutationFn: (payload) => createComment(payload),
    onSuccess: () => {
      message.success(t('comments.createdSuccess'));
      setReplying(false);
      setReplyBody('');
      qc.invalidateQueries({ queryKey });
    },
    onError: (e) => message.error(e.response?.data?.message || t('comments.createError')),
  });

  const update = useMutation({
    mutationFn: (payload) => updateComment(comment.id, payload),
    onSuccess: () => {
      message.success(t('comments.updatedSuccess'));
      setEditing(false);
      qc.invalidateQueries({ queryKey });
    },
    onError: (e) => message.error(e.response?.data?.message || t('comments.updateError')),
  });

  const remove = useMutation({
    mutationFn: () => deleteComment(comment.id),
    onSuccess: () => {
      message.success(t('comments.deletedSuccess'));
      qc.invalidateQueries({ queryKey });
    },
    onError: (e) => message.error(e.response?.data?.message || t('comments.deleteError')),
  });

  const submitReply = () => {
    if (!replyBody.trim()) return;
    reply.mutate({ entityType, entityId, body: replyBody, parent_id: comment.id });
  };

  const submitEdit = () => {
    if (!editBody.trim()) return;
    update.mutate({ body: editBody });
  };

  return (
    <div className="comment-item">
      <div className="comment-item-main">
        <Avatar size="small" style={{ flexShrink: 0 }}>
          {(comment.author_name || '?').charAt(0).toUpperCase()}
        </Avatar>
        <div className="comment-item-content">
          {editing ? (
            <Composer
              value={editBody}
              onChange={setEditBody}
              onSubmit={submitEdit}
              submitting={update.isPending}
              placeholder={t('comments.editPlaceholder')}
            />
          ) : (
            <>
              <div className="comment-item-meta">
                <Text strong>{comment.author_name || `NV #${comment.author_id}`}</Text>
                <Text type="secondary"> · {formatViDateTime(comment.created_at)}</Text>
              </div>
              <RichText html={comment.body} className="comment-body" />
              <Space size={4} className="comment-item-actions">
                <Button type="link" size="small" onClick={() => setReplying((v) => !v)}>
                  {t('comments.reply')}
                </Button>
                {canModify && (
                  <>
                    <Button
                      type="link"
                      size="small"
                      icon={<EditOutlined />}
                      onClick={() => {
                        setEditBody(comment.body);
                        setEditing(true);
                      }}
                    >
                      {t('comments.edit')}
                    </Button>
                    <Popconfirm
                      title={t('comments.deleteConfirm')}
                      okText={t('common.yes')}
                      cancelText={t('common.no')}
                      onConfirm={() => remove.mutate()}
                    >
                      <Button type="link" size="small" danger icon={<DeleteOutlined />}>
                        {t('comments.delete')}
                      </Button>
                    </Popconfirm>
                  </>
                )}
              </Space>
            </>
          )}
          {replying && (
            <Composer
              value={replyBody}
              onChange={setReplyBody}
              onSubmit={submitReply}
              submitting={reply.isPending}
              placeholder={t('comments.replyPlaceholder')}
            />
          )}
        </div>
      </div>
      {comment.replies?.length > 0 && (
        <div className="comment-replies">
          {comment.replies.map((r) => (
            <CommentItem
              key={r.id}
              comment={r}
              entityType={entityType}
              entityId={entityId}
              currentUser={currentUser}
              queryKey={queryKey}
            />
          ))}
        </div>
      )}
    </div>
  );
}

/**
 * @param {object} props
 * @param {string} props.entityType - e.g. 'bill', 'customer', 'depot', 'vehicle'
 * @param {number|string} props.entityId - id of the attached entity
 */
export function CommentSection({ entityType, entityId }) {
  const { currentUser } = useAuth();
  const qc = useQueryClient();
  const queryKey = ['comments', entityType, entityId];

  const { data: comments = [], isLoading } = useQuery({
    queryKey,
    queryFn: () => listComments({ entityType, entityId }),
  });

  const [body, setBody] = useState('');

  const create = useMutation({
    mutationFn: (payload) => createComment(payload),
    onSuccess: () => {
      message.success(t('comments.createdSuccess'));
      setBody('');
      qc.invalidateQueries({ queryKey });
    },
    onError: (e) => message.error(e.response?.data?.message || t('comments.createError')),
  });

  const handleSubmit = () => {
    if (!body.trim()) return;
    create.mutate({ entityType, entityId, body });
  };

  return (
    <Card>
      <div className="bill-block-heading">
        <div>
          <h3>{t('comments.title')}</h3>
          <span>{t('comments.subtitle')}</span>
        </div>
      </div>
      <Composer
        value={body}
        onChange={setBody}
        onSubmit={handleSubmit}
        submitting={create.isPending}
        placeholder={t('comments.placeholder')}
      />
      <Spin spinning={isLoading}>
        {comments.length === 0 ? (
          <Empty image={Empty.PRESENTED_IMAGE_SIMPLE} description={t('comments.empty')} />
        ) : (
          <div className="comment-list">
            {comments.map((c) => (
              <CommentItem
                key={c.id}
                comment={c}
                entityType={entityType}
                entityId={entityId}
                currentUser={currentUser}
                queryKey={queryKey}
              />
            ))}
          </div>
        )}
      </Spin>
    </Card>
  );
}

export default CommentSection;
