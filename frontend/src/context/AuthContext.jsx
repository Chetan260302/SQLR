import { createContext,useContext,useState } from "react";
const AuthContext=createContext();

export const AuthProvider=({children})=>{
    const [token,setToken]=useState(localStorage.getItem('token'));

    const login=(token)=>{
        localStorage.setItem("token",token);
        setToken(token);
    };

    const logout=()=>{
        localStorage.removeItem("token");
        setToken(null);
    };
    function getUsernameFromToken(token) {
        if (!token) return null;
        try {
            const payload = JSON.parse(atob(token.split(".")[1]));
            return payload.sub;
        } catch {
            return null;
        }
    }
    const username=getUsernameFromToken(token);

    return(
        <AuthContext.Provider value={{token,login,logout,username}}>
            {children}
        </AuthContext.Provider>
    );
};

export function useAuth(){
    return useContext(AuthContext);
}