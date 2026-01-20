import { useEffect, useState } from "react";
import { createSession, getDatabases } from "../services/chat";

export default function NewChatModal({ onClose, onCreated }) {
  const [dbs, setDbs] = useState([]);
  const [dbId, setDbId] = useState("");

  useEffect(() => {
    getDatabases().then(res => {
      setDbs(res.data || []);
      if (res.data?.length) setDbId(res.data[0].id);
    });
  }, []);

  const create = async () => {
    if (!dbId) return;
    const res = await createSession(Number(dbId));
    onCreated(res.data);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div className="bg-white w-full max-w-md rounded-lg p-6 space-y-4">
        <h2 className="text-lg font-semibold">New Chat</h2>

        <select
          value={dbId}
          onChange={e => setDbId(e.target.value)}
          className="w-full border rounded px-3 py-2"
        >
          {dbs.map(db => (
            <option key={db.id} value={db.id}>
              {db.name} ({db.dialect})
            </option>
          ))}
        </select>

        <div className="flex justify-end gap-2">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded border"
          >
            Cancel
          </button>
          <button
            onClick={create}
            className="px-4 py-2 rounded bg-blue-600 text-white"
          >
            Create
          </button>
        </div>
      </div>
    </div>
  );
}
