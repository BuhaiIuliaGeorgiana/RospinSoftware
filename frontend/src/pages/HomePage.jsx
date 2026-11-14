import { Link } from "react-router";
import { useState } from "react";
import { logout } from "../services/authService";
function HomePage(){
    const [error,setError] = useState("");

    async function handleLogout(){
        setError("");

        try{
            const response = await logout();
            if(result.error){
                setError(result.error.message);
            }
        } catch(err) {
            setError(err.message || "Logout failed");
        }
    }
    return(
        <div>
            <h1>Welcome to FloodLens!</h1>
            <p>
            <Link to="/signup">Sign up</Link>
            </p>
            <p>
            <Link to="/login">Log in</Link>
            </p>

            <p>
                <button onClick = {handleLogout}>  Log out </button>
                {error && <p role = "alert">{error}</p>}
            </p>
        </div>
    )
}

export default HomePage;