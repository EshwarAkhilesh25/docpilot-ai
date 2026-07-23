import { memo } from "react";
import ReactMarkdown from "react-markdown";
import type { Components } from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeRaw from "rehype-raw";
import rehypeSanitize from "rehype-sanitize";
import { CodeBlock } from "./CodeBlock";
import { cn } from "@lib/utils";

interface MarkdownRendererProps {
  content: string;
  className?: string;
}

// Memoize plugins to avoid recreation on each render
const remarkPlugins = [remarkGfm];
const rehypePlugins = [rehypeRaw, rehypeSanitize];

// Memoize component mapping to avoid recreation on each render
const components: Components = {
  code({ className, children, ...props }) {
    const match = /language-(\w+)/.exec(className || "");
    const language = match ? match[1] : "";
    // react-markdown v8+ does not pass `inline` — detect it by absence of language match
    const isBlock = Boolean(match);

    if (isBlock) {
      return (
        <CodeBlock
          language={language}
          code={String(children).replace(/\n$/, "")}
          className="my-4"
        />
      );
    }

    return (
      <code
        className={cn(
          className,
          "bg-muted px-1.5 py-0.5 rounded font-mono text-xs",
        )}
        {...props}
      >
        {children}
      </code>
    );
  },
  a({ href, children, ...props }) {
    return (
      <a
        href={href}
        target="_blank"
        rel="noopener noreferrer"
        className="text-primary hover:underline"
        {...props}
      >
        {children}
      </a>
    );
  },
};

const MarkdownRenderer = memo(
  ({ content, className }: MarkdownRendererProps) => {
    return (
      <div
        className={cn(
          "prose prose-sm dark:prose-invert max-w-none",
          "prose-headings:font-semibold prose-headings:tracking-tight",
          "prose-h1:text-xl prose-h2:text-lg prose-h3:text-base",
          "prose-p:text-sm prose-p:leading-relaxed",
          "prose-strong:font-semibold",
          "prose-em:italic",
          "prose-ul:list-disc prose-ol:list-decimal",
          "prose-li:my-1 prose-li:pl-1",
          "prose-blockquote:border-l-4 prose-blockquote:border-muted-foreground/20 prose-blockquote:pl-4 prose-blockquote:italic",
          "prose-code:bg-muted prose-code:px-1.5 prose-code:py-0.5 prose-code:rounded prose-code:font-mono prose-code:text-xs",
          "prose-pre:bg-background prose-pre:border prose-pre:border-border",
          "prose-table:text-sm prose-table:border-collapse",
          "prose-th:border prose-th:border-border prose-th:px-3 prose-th:py-2 prose-th:bg-muted",
          "prose-td:border prose-td:border-border prose-td:px-3 prose-td:py-2",
          className,
        )}
      >
        <ReactMarkdown
          remarkPlugins={remarkPlugins}
          rehypePlugins={rehypePlugins}
          components={components}
        >
          {content}
        </ReactMarkdown>
      </div>
    );
  },
);

MarkdownRenderer.displayName = "MarkdownRenderer";

export default MarkdownRenderer;
