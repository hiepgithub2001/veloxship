/**
 * RichText — safely render sanitized rich-text (HTML) content.
 *
 * Backend already sanitizes comment bodies with a strict whitelist; this is a
 * second (defense-in-depth) sanitize pass on the client before injecting HTML.
 */
import DOMPurify from 'dompurify';

const ALLOWED_TAGS = [
  'p',
  'br',
  'strong',
  'b',
  'em',
  'i',
  'u',
  's',
  'strike',
  'ul',
  'ol',
  'li',
  'blockquote',
  'code',
  'pre',
  'h1',
  'h2',
  'h3',
  'a',
  'hr',
  'img',
];

const ALLOWED_ATTR = ['href', 'target', 'rel', 'src', 'alt', 'title'];

/**
 * @param {object} props
 * @param {string} [props.html=''] - HTML content to render
 * @param {string} [props.className] - additional CSS class
 */
export function RichText({ html = '', className }) {
  const clean = DOMPurify.sanitize(html, {
    ALLOWED_TAGS,
    ALLOWED_ATTR,
    ALLOWED_URI_REGEXP: /^(?:(?:https?|mailto):|[^a-z]|[a-z+.-]+(?:[^a-z+.-:]|$))/i,
  });

  return (
    <div
      className={className ? `rich-text ${className}` : 'rich-text'}
      dangerouslySetInnerHTML={{ __html: clean }}
    />
  );
}

export default RichText;
