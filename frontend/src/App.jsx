import { Routes, Route, Navigate } from "react-router-dom";
import Login from "./pages/Login";
import Chat from "./pages/ChatPage";
import { useAuth } from "./context/AuthContext";
import Signup from "./pages/Signup";

function App() {
  const { token } = useAuth();

  return (
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup/>}/>
        <Route
          path="/chat"
          element={token ? <Chat /> : <Navigate to="/login" />}
        />
        <Route path="*" element={<Navigate to="/login" />} />
        
      </Routes>
  );
}

export default App;
