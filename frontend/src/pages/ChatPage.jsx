import { useEffect, useState } from "react";
import Sidebar from "../components/Sidebar";
import ChatWindow from "../components/ChatWindow";
import ChatInput from "../components/ChatInput";
import AddDatabaseModal from "../components/AddDatabaseModal";
import NewChatModal from "../components/NewChatModal";
import {
  getSessions,
  getMessages,
  deleteSession,
  streamChatMessage
} from "../services/chat";

export default function ChatPage() {
  const [sessions, setSessions] = useState([]);
  const [currentSession, setCurrentSession] = useState(null);
  const [messages, setMessages] = useState([]);
  const [showAddDb, setShowAddDb] = useState(false);
  const [showNewChat, setShowNewChat] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [isStreaming, setIsStreaming] = useState(false);


  useEffect(() => {
    loadSessions();
  }, []);

  useEffect(() => {
    if (!currentSession?.id) return;
    loadMessages();
  }, [currentSession?.id]);

  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth < 768) setSidebarOpen(false);
      else setSidebarOpen(true);
    };
    handleResize();
    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);


  const loadSessions = async () => {
    const res = await getSessions();
    setSessions(res.data);
  };

  const loadMessages = async () => {
    const res = await getMessages(currentSession.id);
    setMessages(prev => {
      const map = new Map();

      [...prev, ...res.data].forEach(m => {
        map.set(m.id, m);
      });

      return Array.from(map.values());
    });
  };

  /* -------------------- ACTIONS -------------------- */

  const newChat = () => {
    setShowNewChat(true);
  };

  const handleChatCreated = (session) => {
    setSessions((prev) => [session, ...prev]);
    setCurrentSession(session);
    setMessages([]);
  };

  const selectSession = (session) => {
    setCurrentSession(session);
  };

  const send = async (text) => {
    if (!currentSession?.id) return;

    const userMsg = {
      id: `temp-user-${crypto.randomUUID()}`,
      role: "user",
      content: text,
    };

    const assistantMsg = {
      id: `temp-assistant-${crypto.randomUUID()}`,
      role: "assistant",
      content: "",
    };

    setMessages((prev) => [...prev, userMsg, assistantMsg]);
    setIsStreaming(true);

    let assistantText = "";


    await streamChatMessage(
      currentSession.id,
      text,
      (chunk,meta) => {
        console.log("stream meta:",meta)
        
        if (chunk.includes("__META__")) {
          const [metaPart, rest] = chunk.split("__END_META__");

          try {
            const meta = JSON.parse(
              metaPart.replace("__META__", "").trim()
            );

            if (meta.session_title) {
              setSessions(prev =>
                prev.map(s =>
                  s.id === currentSession.id
                    ? { ...s, title: meta.session_title }
                    : s
                )
              );

              setCurrentSession(s => ({
                ...s,
                title: meta.session_title
              }));
            }
          } catch (e) {
            console.error("META parse failed:", e, metaPart);
          }

          if (!rest) return;
          chunk = rest;
        }

        assistantText += chunk;

        setMessages((prev) => {
          const updated = [...prev];
          updated[updated.length - 1] = {
            ...updated[updated.length - 1],
            content: assistantText
          };

          return updated;
        });
      }
    );
  
    setIsStreaming(false);
  };


  const deleteChat = async (sessionId) => {
    await deleteSession(sessionId);
    setSessions((prev) => prev.filter((s) => s.id !== sessionId));
    if (currentSession?.id === sessionId) {
      setCurrentSession(null);
      setMessages([]);
    }
  };

  /* -------------------- RENDER -------------------- */

  return (
    <div className="h-screen flex flex-col bg-gray-100 overflow-hidden">
      
      {/* 🔹 TOP HEADER (ALWAYS VISIBLE) */}
          <div className="h-12 flex items-center border-b border-gray-300 bg-white px-4 sticky top-0 z-50">
            <button
              onClick={() => setSidebarOpen((v) => !v)}
              className="text-xl text-gray-600 hover:text-black"
            >
              {sidebarOpen ? "✕" : "☰"}
            </button>

            
          </div>
      <div className="flex flex-1 overflow-hidden">

  {/* SIDEBAR */}
  {sidebarOpen && (
    <div
      className={`
        fixed md:relative
        inset-y-0 left-0
        w-64
        bg-white
        border-r border-gray-200
        z-50
        overflow-y-auto
        overflow-x-hidden
        md:translate-x-0
        transition-transform duration-300
        ${sidebarOpen ? "translate-x-0" : "-translate-x-full"}
      `}
    >
      <Sidebar
        sessions={sessions}
        onSelect={selectSession}
        onNewChat={newChat}
        onDelete={deleteChat}
        onAddDatabase={() => setShowAddDb(true)}
        onClose={()=>setSidebarOpen(false)}
      />
    </div>
  )}

  {/* CHAT AREA */}
<div className="flex-1 flex flex-col min-w-0 bg-white relative overflow-hidden">
  {!currentSession ? (
    /* NO SESSION SELECTED */
    <div className="flex-1 flex items-center justify-center text-gray-500">
      Select or create a chat
    </div>
  ) : (
    /* SESSION ACTIVE - This container handles both empty and full chats */
    <>
      {/* 1. SCROLLABLE AREA */}
      <div className="flex-1 overflow-y-auto">
        {messages.length === 0 ? (
          <div className="flex h-full items-center justify-center text-gray-400">
            {/* You can put a logo or "How can I help you?" here */}
            Ask something to start the conversation...
          </div>
        ) : (
          <div className="mx-auto w-full max-w-4xl px-4 md:px-6">
            <ChatWindow messages={messages} isStreaming={isStreaming}/>
          </div>
        )}
      </div>

      {/* 2. FLOATING INPUT AREA (Respects Sidebar) */}
      <div className="w-full pb-6 pt-2">
        <div className="mx-auto max-w-3xl lg:max-w-4xl px-4">
          {/* Note: No 'fixed' class here, so it stays inside the Chat Area */}
          <ChatInput onSend={send} disabled={false} />
        </div>
      </div>
    </>
  )}
</div>
    
  </div>
      {/* MODALS */}
      {showAddDb && <AddDatabaseModal onClose={() => setShowAddDb(false)} />}
      {showNewChat && (
        <NewChatModal
          onClose={() => setShowNewChat(false)}
          onCreated={handleChatCreated}
        />
      )}
    </div>
  );
}
