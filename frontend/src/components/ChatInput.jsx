import { useState } from "react";

export default function ChatInput({ onSend, disabled }) {
  const [text, setText] = useState("");

  const handleSend = async () => {
    if (!text.trim() || disabled) return;
    await onSend(text);
    setText("");
  };

  // Handle "Enter" key to send message
  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="pb-safe">
    <div className="w-full">
      <div className="mx-auto max-w-3xl lg:max-w-4xl">
        <div className={`flex items-center gap-3 rounded-full border border-gray-200 bg-white px-6 py-3 shadow-2xl transition-all ${disabled ? "opacity-50" : "focus-within:ring-2 focus-within:ring-blue-500"}`}>
          
          <input
            className="flex-grow bg-transparent text-gray-700 outline-none placeholder:text-gray-400"
            value={text}
            onChange={(e) => setText(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={disabled}
            placeholder={disabled ? "Create a Chat first" : "Ask something..."}
          />

          <button
            onClick={handleSend}
            disabled={disabled || !text.trim()}
            className={`rounded-full px-4 py-2 text-sm font-semibold transition-colors 
              ${text.trim() && !disabled 
                ? "bg-blue-600 text-white hover:bg-blue-700" 
                : "bg-gray-100 text-gray-400 cursor-not-allowed"}`}
          >
            Send
          </button>
          
        </div>
      </div>
    </div>
    </div>
  );
}