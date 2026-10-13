import type { ReactNode } from 'react';

function normalizeSourceText(value: string | null) {
  return (value ?? '')
    .replace(/\uFFFD+/g, ' ')
    .replace(/\b(Couldn|doesn|isn|aren|wasn|weren|wouldn|shouldn|didn|haven|hasn|hadn)\s+t\b/gi, "$1't")
    .replace(/\s+/g, ' ');
}

function renderSafeNode(node: Node, key: string): ReactNode {
  if (node.nodeType === Node.TEXT_NODE) return normalizeSourceText(node.textContent);
  if (!(node instanceof HTMLElement)) return null;

  const children = Array.from(node.childNodes).map((child, index) =>
    renderSafeNode(child, `${key}-${index}`)
  );

  if (node.tagName === 'B' || node.tagName === 'STRONG') {
    return <mark key={key} className="rounded bg-[#dceee5] px-1 font-semibold text-[#20594e]">{children}</mark>;
  }

  return <span key={key}>{children}</span>;
}

/** Search excerpts contain server-side <b> markers. Render only text and emphasis safely. */
export function HighlightedExcerpt({ html }: { html: string }) {
  const parsed = new DOMParser().parseFromString(html, 'text/html');
  return <>{Array.from(parsed.body.childNodes).map((node, index) => renderSafeNode(node, `excerpt-${index}`))}</>;
}
