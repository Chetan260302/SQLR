import api from "./api";

export const getSessions=()=>api.get("/chat/sessions");
export const createSession=(dbId)=>api.post("/chat/sessions",{title:"New Chat",db_id:dbId});

export const getMessages=(sessionId) =>
    api.get(`/chat/${sessionId}/messages`);

export const sendMessage=(sessionId,message) =>
    api.post(`/chat/${sessionId}/messages`,{message});

export const deleteSession=(sessionId)=>
    api.delete(`/chat/sessions/${sessionId}`);

export const getDatabases=()=>
    api.get("/databases");

export const createDatabase = (payload) =>
  api.post("/databases", payload);

export const testDatabase=(payload)=>
    api.post("/databases/test",payload)


export async function streamChatMessage(sessionId, message, onChunk) {
  const token = localStorage.getItem("token");

  const res = await fetch(
    `http://localhost:8000/chat/${sessionId}/messages`,
    {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ message }),
    }
  );

  if (!res.body) {
    throw new Error("Streaming not supported");
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder("utf-8");

  let done = false;

  while (!done) {
    const { value, done: doneReading } = await reader.read();
    done = doneReading;

    if (value) {
      const chunk = decoder.decode(value, { stream: true });
      onChunk(chunk);
    }
  }
}
