import type { FC } from 'react';
import ReactMarkdown, { type Components } from 'react-markdown';
import remarkGfm from 'remark-gfm';

interface MarkdownViewProps {
  content: string;
  className?: string;
}

const markdownComponents: Components = {
  a: ({ href, children, ...props }) => {
    const isExternal = href?.startsWith('https://') || href?.startsWith('http://');
    return (
      <a
        href={href}
        {...(isExternal ? { target: '_blank', rel: 'noreferrer noopener' } : {})}
        {...props}
      >
        {children}
      </a>
    );
  },
  img: () => null,
};

/** Render policy text as CommonMark/GFM without enabling raw HTML. */
export const MarkdownView: FC<MarkdownViewProps> = ({ content, className = '' }) => {
  if (!content?.trim()) return null;
  const normalizedContent = content
    .replace(/\r\n?/g, '\n')
    .replace(/[\u0000-\u0008\u000B\u000C\u000E-\u001F\u007F]/g, '');

  return (
    <div className={`prose-policy ${className}`.trim()}>
      <ReactMarkdown remarkPlugins={[remarkGfm]} components={markdownComponents}>
        {normalizedContent}
      </ReactMarkdown>
    </div>
  );
};
