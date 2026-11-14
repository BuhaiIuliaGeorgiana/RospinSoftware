import { useState } from "react";

import { useAuth } from "../hooks/useAuth";
import { logout } from "../services/authService";

function HomePage(){
    const {user} = useAuth();
    const [error,setError] = useState("");

    async function handleLogout(){
        setError("");

        try{
            const result = await logout();

            if(result.error){
                setError(result.error.message);
            }
        }catch(err){
            setError(err.message || "Logout failed");
        }
    }

    return(
        <div>
            <h1>Flood Assessment</h1>
            <p>Logged in as: {user?.email}</p>

            <button onClick={handleLogout}>
                Logout
            </button>

            {error && <p role="alert">{error}</p>}
        </div>
    );
}

export default HomePage;