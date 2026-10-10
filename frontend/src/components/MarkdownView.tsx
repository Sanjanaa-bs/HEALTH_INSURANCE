import React from 'react';

interface MarkdownViewProps {
  content: string;
  className?: string;
}

/**
 * A lightweight, safe Markdown renderer that formats bold (**text**),
 * bullet points (- or *), section headings, and clean paragraph breaks
 * without displaying literal markdown syntax.
 */
export const MarkdownView: React.FC<MarkdownViewProps> = ({ content, className = '' }) => {
  if (!content) return null;

  // Split content into blocks by double newlines or single newlines
  const lines = content.split('\n');

  // Helper to parse inline bold and code
  const renderInline = (text: string): React.ReactNode[] => {
    // Regex matching **bold** or *italic*
    const parts = text.split(/(\*\*[^*]+\*\*)/g);
    return parts.map((part, index) => {
      if (part.startsWith('**') && part.endsWith('**')) {
        return (
          <strong key={index} className="font-semibold text-white">
            {part.slice(2, -2)}
          </strong>
        );
      }
      return <React.Fragment key={index}>{part}</React.Fragment>;
    });
  };

  const elements: React.ReactNode[] = [];
  let currentList: string[] = [];

  const flushList = () => {
    if (currentList.length > 0) {
      elements.push(
        <ul key={`ul-${elements.length}`} className="my-2.5 space-y-2 pl-4 list-disc marker:text-cyan-400">
          {currentList.map((item, i) => (
            <li key={i} className="text-slate-200 text-sm leading-relaxed">
              {renderInline(item)}
            </li>
          ))}
        </ul>
      );
      currentList = [];
    }
  };

  for (let i = 0; i < lines.length; i++) {
    const rawLine = lines[i];
    const trimmed = rawLine.trim();

    if (!trimmed) {
      flushList();
      continue;
    }

    // Check for bullet list item: starts with "- " or "* "
    if (trimmed.startsWith('- ') || trimmed.startsWith('* ')) {
      currentList.push(trimmed.slice(2).trim());
      continue;
    }

    flushList();

    // Check for section title starting with "**" and ending with "**" or containing colon
    if (trimmed.startsWith('**') && trimmed.endsWith('**')) {
      elements.push(
        <h4 key={i} className="font-bold text-white text-base mt-3.5 mb-1.5 text-cyan-200">
          {trimmed.slice(2, -2)}
        </h4>
      );
    } else {
      elements.push(
        <p key={i} className="text-slate-200 text-sm leading-relaxed my-2">
          {renderInline(trimmed)}
        </p>
      );
    }
  }

  flushList();

  return <div className={`space-y-1 ${className}`}>{elements}</div>;
};
