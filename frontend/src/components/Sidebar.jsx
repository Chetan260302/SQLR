import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Sidebar({
  sessions,
  onSelect,
  onNewChat,
  onDelete,
  onAddDatabase,
  onClose
})

{
  const {logout }=useAuth();
  const navigate =useNavigate();

  console.log("Auth context:", useAuth());

  const handleLogout=()=>{
    logout();
    navigate("/login");
  }
  return (
    
    <div className="h-full flex flex-col p-3 overflow-y-auto">
      <div className="md:hidden flex justify-end p-2">
        <button
          onClick={onClose}
          className="text-xl text-gray-600"
          aria-label="Close sidebar"
        >
          ✕
        </button>
      </div>
      
      <button
        onClick={onNewChat}
        className="mb-2 px-3 py-2 rounded bg-blue-600 text-white"
      >
        + New Chat
      </button>

      <button
        onClick={onAddDatabase}
        className="mb-4 px-3 py-2 rounded border"
      >
        + Add Database
      </button>

      <div className="space-y-1">
        {sessions.map((s) => (
          <div
            key={s.id}
            onClick={() => onSelect(s)}
            className="relative group flex items-center gap-2 px-2 py-1 rounded cursor-pointer hover:bg-gray-100"
          >
            <div className="flex-1 truncate px-2">
            {s.title || "New Chat"}

            {/* TOOLTIP */}
            {s.title && (
              <div
                className="
                  pointer-events-none
                  absolute left-full top-1/2 -translate-y-1/2 ml-2
                  hidden group-hover:block
                  w-max max-w-xs
                  rounded
                  bg-black
                  text-white
                  text-xs
                  px-3 py-2
                  shadow-lg
                  z-[9999]
                  whitespace-normal
                "
              >
                {s.title}
              </div>

            )}
          </div>

            <button
              onClick={(e) => {
                e.stopPropagation();
                onDelete(s.id);
              }}
              className="ml-2 text-gray-400 hover:text-red-600"
            >
              ✕
            </button>
          </div>
        ))}
      </div>
      <button
        onClick={handleLogout}
        className="mt-4 px-3 py-2 rounded border text-sm text-red-600 hover:bg-red-50"
      >
        Logout
      </button>
    </div>
  );
}
