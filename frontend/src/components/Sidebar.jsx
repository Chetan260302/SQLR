import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import {LogOut} from "lucide-react";

export default function Sidebar({
  sessions,
  onSelect,
  onNewChat,
  onDelete,
  onAddDatabase,
  onClose
})

{
  const {username,logout }=useAuth();
  const navigate =useNavigate();

  console.log("Auth context:", useAuth());

  const handleLogout=()=>{
    logout();
    navigate("/login");
  }
  return (
    <div className="h-full flex flex-col bg-white border-r">

      {/* 🔹 TOP (Scrollable) */}
      <div className="flex-1 overflow-y-auto p-3">

        {/* Mobile close */}
        <div className="md:hidden flex justify-end mb-2">
          <button
            onClick={onClose}
            className="text-xl text-gray-600"
          >
            ✕
          </button>
        </div>

        <button
          onClick={onNewChat}
          className="mb-2 w-full px-3 py-2 rounded bg-blue-600 text-white"
        >
          + New Chat
        </button>

        <button
          onClick={onAddDatabase}
          className="mb-4 w-full px-3 py-2 rounded border"
        >
          + Add Database
        </button>

        {/* Sessions */}
        <div className="space-y-1">
          {sessions.map((s) => (
            <div
              key={s.id}
              onClick={() => onSelect(s)}
              className="group relative flex items-center px-2 py-1 rounded cursor-pointer hover:bg-gray-100"
            >
              <div className="flex-1 truncate">
                {s.title || "New Chat"}
              </div>

              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onDelete(s.id);
                }}
                className="text-gray-400 hover:text-red-600"
              >
                ✕
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* 🔹 BOTTOM (Fixed Footer) */}
      <div className="border-t px-4 py-3 flex items-center justify-between">
        <div className="text-sm text-gray-600 truncate">
          Logged in as
          <div className="font-medium text-gray-800">
            {username || "User"}
          </div>
        </div>

        <button
          onClick={handleLogout}
          className="text-gray-500 hover:text-red-600"
          title="Logout"
        >
          <LogOut size={18} />
        </button>
      </div>
    </div>
  );

}
