/**
 * RichTextEditor — TipTap rich-text editor with a compact toolbar.
 *
 * Controlled component: `value` is an HTML string, `onChange` emits HTML
 * (empty string when the editor has no text and no image). Toolbar exposes
 * common inline/block formatting plus inline image insertion via TipTap's
 * native Image extension (images are uploaded through `onUploadImage`).
 */
import { useEffect, useRef, useState } from 'react';
import { EditorContent, useEditor } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import Placeholder from '@tiptap/extension-placeholder';
import Image from '@tiptap/extension-image';
import { Button, Space, message } from 'antd';
import {
  BoldOutlined,
  ItalicOutlined,
  StrikethroughOutlined,
  UnorderedListOutlined,
  OrderedListOutlined,
  BlockOutlined,
  CodeOutlined,
  UndoOutlined,
  RedoOutlined,
  PictureOutlined,
} from '@ant-design/icons';

function ToolbarButton({ active, onClick, disabled, icon, title }) {
  return (
    <Button
      size="small"
      type={active ? 'primary' : 'text'}
      onClick={onClick}
      onMouseDown={(e) => e.preventDefault()}
      disabled={disabled}
      title={title}
      icon={icon}
    />
  );
}

function HeadingButton({ level, active, onClick, disabled }) {
  return (
    <Button
      size="small"
      type={active ? 'primary' : 'text'}
      onClick={onClick}
      onMouseDown={(e) => e.preventDefault()}
      disabled={disabled}
    >
      H{level}
    </Button>
  );
}

const isEmptyHtml = (html) =>
  !html || (!html.replace(/<[^>]*>/g, '').trim() && !html.includes('<img'));

/**
 * @param {object} props
 * @param {string} [props.value=''] - HTML content
 * @param {(html: string) => void} [props.onChange]
 * @param {string} [props.placeholder]
 * @param {boolean} [props.disabled=false]
 * @param {(file: File) => Promise<string>} [props.onUploadImage] - uploads a file and
 *   resolves to a displayable image URL; enables the inline-image button when provided
 */
export function RichTextEditor({ value = '', onChange, placeholder, disabled = false, onUploadImage }) {
  const fileInputRef = useRef(null);
  const [uploading, setUploading] = useState(false);

  const editor = useEditor({
    extensions: [
      StarterKit.configure({ heading: { levels: [2, 3] } }),
      Placeholder.configure({ placeholder: placeholder || '' }),
      Image.configure({ inline: false, allowBase64: false }),
    ],
    content: value || '',
    editable: !disabled,
    onUpdate: ({ editor }) => {
      const html = editor.getHTML();
      const hasContent = editor.getText().trim() !== '' || html.includes('<img');
      onChange?.(hasContent ? html : '');
    },
  });

  // Keep the editor in sync when `value` changes externally (e.g. opening edit mode).
  useEffect(() => {
    if (!editor) return;
    const current = editor.getHTML();
    if (isEmptyHtml(current) && isEmptyHtml(value)) return;
    if (current !== value) {
      editor.commands.setContent(value || '', false);
    }
  }, [editor, value]);

  // Toggle editability without recreating the editor.
  useEffect(() => {
    editor?.setEditable(!disabled);
  }, [editor, disabled]);

  const handleFileSelect = async (event) => {
    const file = event.target.files?.[0];
    event.target.value = '';
    if (!file || !onUploadImage || !editor) return;
    setUploading(true);
    try {
      const url = await onUploadImage(file);
      if (url) {
        editor.chain().focus().setImage({ src: url }).run();
      }
    } catch {
      message.error('Tải ảnh lên thất bại');
    } finally {
      setUploading(false);
    }
  };

  if (!editor) return null;

  return (
    <div className="rich-text-editor">
      <Space size={2} className="rich-text-toolbar" wrap>
        <ToolbarButton
          icon={<BoldOutlined />}
          title="Đậm"
          disabled={disabled}
          active={editor.isActive('bold')}
          onClick={() => editor.chain().focus().toggleBold().run()}
        />
        <ToolbarButton
          icon={<ItalicOutlined />}
          title="Nghiêng"
          disabled={disabled}
          active={editor.isActive('italic')}
          onClick={() => editor.chain().focus().toggleItalic().run()}
        />
        <ToolbarButton
          icon={<StrikethroughOutlined />}
          title="Gạch ngang"
          disabled={disabled}
          active={editor.isActive('strike')}
          onClick={() => editor.chain().focus().toggleStrike().run()}
        />
        <HeadingButton
          level={2}
          disabled={disabled}
          active={editor.isActive('heading', { level: 2 })}
          onClick={() => editor.chain().focus().toggleHeading({ level: 2 }).run()}
        />
        <HeadingButton
          level={3}
          disabled={disabled}
          active={editor.isActive('heading', { level: 3 })}
          onClick={() => editor.chain().focus().toggleHeading({ level: 3 }).run()}
        />
        <ToolbarButton
          icon={<UnorderedListOutlined />}
          title="Danh sách"
          disabled={disabled}
          active={editor.isActive('bulletList')}
          onClick={() => editor.chain().focus().toggleBulletList().run()}
        />
        <ToolbarButton
          icon={<OrderedListOutlined />}
          title="Danh sách số"
          disabled={disabled}
          active={editor.isActive('orderedList')}
          onClick={() => editor.chain().focus().toggleOrderedList().run()}
        />
        <ToolbarButton
          icon={<BlockOutlined />}
          title="Trích dẫn"
          disabled={disabled}
          active={editor.isActive('blockquote')}
          onClick={() => editor.chain().focus().toggleBlockquote().run()}
        />
        <ToolbarButton
          icon={<CodeOutlined />}
          title="Code"
          disabled={disabled}
          active={editor.isActive('code')}
          onClick={() => editor.chain().focus().toggleCode().run()}
        />
        {onUploadImage && (
          <ToolbarButton
            icon={<PictureOutlined />}
            title="Chèn ảnh"
            disabled={disabled || uploading}
            onClick={() => fileInputRef.current?.click()}
          />
        )}
        <ToolbarButton
          icon={<UndoOutlined />}
          title="Hoàn tác"
          disabled={disabled || !editor.can().undo()}
          onClick={() => editor.chain().focus().undo().run()}
        />
        <ToolbarButton
          icon={<RedoOutlined />}
          title="Làm lại"
          disabled={disabled || !editor.can().redo()}
          onClick={() => editor.chain().focus().redo().run()}
        />
      </Space>
      <input ref={fileInputRef} type="file" accept="image/*" hidden onChange={handleFileSelect} />
      <EditorContent editor={editor} />
    </div>
  );
}

export default RichTextEditor;
