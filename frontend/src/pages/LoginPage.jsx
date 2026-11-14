import { Link, useNavigate } from "react-router";
import { useState } from "react";
import { login } from "../services/authService";

function LoginPage() {
    const [email,setEmail] = useState("");
    const [password,setPassword] = useState("");
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(false);

    const navigate = useNavigate();
    async function handleLogin(event){
        event.preventDefault();

        setLoading(true)
        console.log("Email:", email);
        console.log("Login form submitted");
        

        try{
            const result = await login(email,password)

            if(result.error){
                setError(result.error.message);
                return;
            }

            navigate("/");
        }catch(err){
            setError(err.message || "An unexpected error occured.");
        }finally{
            setLoading(false);
        }
    }
    return (
        <div>
            <h1>Login Page</h1>

            <form onSubmit = {handleLogin}>
                <label htmlFor="email">Email:</label>
                    <input  id="email"
                            value = {email}
                            type="email"
                            onChange={(e)=>setEmail(e.target.value)} 
                            required
                            />

                <label htmlFor="password">Password:</label>
                    <input  id="password" 
                            type="password"
                            value = {password}
                            onChange={(e)=>setPassword(e.target.value)} 
                            required
                            />

                <button type="submit" disabled = {loading} >
                    {loading ? "Logging in..." : "Login"}
                </button>
            </form>

            <p>
                Don't have an account?
                <Link to="/signup">Sign up</Link>
            </p>
        </div>
    );
}

export default LoginPage;