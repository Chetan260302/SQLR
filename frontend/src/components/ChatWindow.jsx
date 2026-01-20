import { useEffect, useRef } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import TypingDots from "./TypingDots";

export default function ChatWindow({ messages, isStreaming }) {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isStreaming]);

  return (
    <div className="space-y-6 py-6">
      {messages.map((m, i) => {
        const isUser = m.role === "user";
        const isLastAssistant =
          !isUser && i === messages.length - 1 && isStreaming;

        return (
          <div
            key={i}
            className={`flex ${isUser ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`
                ${isUser ? "max-w-[70%]" : "max-w-[85%]"}
                rounded-2xl
                px-5
                py-4
                text-base
                leading-relaxed
                ${isUser
                  ? "bg-gray-200 text-gray-900"
                  : "bg-white border border-gray-200"}
              `}
            >
              <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                components={{
                  table({ children }) {
                    return (
                      <div className="overflow-x-auto my-3">
                        <table className="min-w-max border-collapse text-sm">
                          {children}
                        </table>
                      </div>
                    );
                  },

                  th({ children }) {
                    return (
                      <th className="border border-gray-300 bg-gray-100 px-3 py-2 text-left font-semibold whitespace-nowrap">
                        {children}
                      </th>
                    );
                  },

                  td({ children }) {
                    return (
                      <td className="border border-gray-300 px-3 py-2 whitespace-nowrap">
                        {children}
                      </td>
                    );
                  },

                  h2: ({ children }) => (
                    <h2 className="text-xl font-semibold mt-5 mb-2">{children}</h2>
                  ),
                  h3: ({ children }) => (
                    <h3 className="text-lg font-semibold mt-4 mb-1">{children}</h3>
                  ),
                  p: ({ children }) => (
                    <p className="mb-3 last:mb-0">{children}</p>
                  ),
                  ul: ({ children }) => (
                    <ul className="list-disc pl-6 mb-3 space-y-1">{children}</ul>
                  ),
                  code({ inline, className, children }) {
                    const text = String(children).trim();
                    const isSql =
                      className?.includes("sql") ||
                      text.toLowerCase().startsWith("select") ||
                      text.toLowerCase().startsWith("with");

                    if (inline) {
                      return (
                        <code className="px-1 py-0.5 bg-gray-100 rounded text-xs">
                          {children}
                        </code>
                      );
                    }

                    return (
                      <div className="relative group">
                        {isSql && (
                          <button
                            onClick={() => navigator.clipboard.writeText(text)}
                            className="
                              absolute top-2 right-2
                              text-xs
                              bg-gray-200
                              hover:bg-gray-300
                              px-2 py-1
                              rounded
                              opacity-0 group-hover:opacity-100
                              transition
                            "
                          >
                            Copy
                          </button>
                        )}

                        <pre className="bg-gray-100 rounded p-4 text-sm overflow-x-auto">
                          <code>{children}</code>
                        </pre>
                      </div>
                    );
                  }

                }}
              >
                {m.content}
              </ReactMarkdown>

              {/* ▍ Streaming cursor */}
              {isLastAssistant && (
                <span className="inline-block ml-1 animate-pulse font-mono">
                  ▍
                </span>
              )}
            </div>
          </div>
        );
      })}

      {/* Thinking dots before first token */}
      {isStreaming &&
        messages.length > 0 &&
        messages[messages.length - 1].content === "" && (
          <div className="flex justify-start">
            <div className="bg-white border border-gray-200 rounded-2xl max-w-[85%]">
              <TypingDots />
            </div>
          </div>
        )}

      <div ref={bottomRef} />
    </div>
  );
}
