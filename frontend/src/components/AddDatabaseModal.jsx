import { useState } from "react";
import { createDatabase, testDatabase } from "../services/chat";

export default function AddDatabaseModal({ onClose, onCreated }) {
  const [name, setName] = useState("");
  const [dialect, setDialect] = useState("sqlite");
  const [uri, setUri] = useState("");
  const [tested, setTested] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const testConnection = async () => {
    setLoading(true);
    setError("");
    try {
      const res = await testDatabase({ name, dialect, connection_uri: uri });
      if (res.data.ok) setTested(true);
      else setError(res.data.error || "Test failed");
    } catch {
      setError("Test failed");
    } finally {
      setLoading(false);
    }
  };

  const submit = async () => {
    if (!tested) return;
    await createDatabase({ name, dialect, connection_uri: uri });
    onCreated?.();
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div className="bg-white w-full max-w-md rounded-lg p-6 space-y-3">
        <h2 className="text-lg font-semibold">Add Database</h2>

        {error && <p className="text-red-600 text-sm">{error}</p>}
        {tested && <p className="text-green-600 text-sm">Connection OK</p>}

        <input
          className="w-full border px-3 py-2 rounded"
          placeholder="Database name"
          value={name}
          onChange={e => setName(e.target.value)}
        />

        <select
          className="w-full border px-3 py-2 rounded"
          value={dialect}
          onChange={e => setDialect(e.target.value)}
        >
          <option value="sqlite">SQLite</option>
          <option value="postgresql">PostgreSQL</option>
          <option value="mysql">MySQL</option>
          <option value="mssql">SQL Server</option>
        </select>

        <input
          className="w-full border px-3 py-2 rounded"
          placeholder="Connection URI"
          value={uri}
          onChange={e => {
            setUri(e.target.value);
            setTested(false);
          }}
        />

        <div className="flex justify-end gap-2 pt-2">
          <button className="border px-3 py-2 rounded" onClick={onClose}>
            Cancel
          </button>
          <button
            onClick={testConnection}
            className="border px-3 py-2 rounded"
          >
            Test
          </button>
          <button
            onClick={submit}
            disabled={!tested}
            className="bg-blue-600 text-white px-4 py-2 rounded disabled:opacity-50"
          >
            Add
          </button>
        </div>
      </div>
    </div>
  );
}
