import { Link } from "react-router";
import { useState } from "react";


function LoginPage() {
    const [email,setEmail] = useState("");
    const [password,setPassword] = useState("");

    function handleLogin(event){
        event.preventDefault();
        console.log("Email:", email);
        console.log("Login form submitted");
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

                <button type="submit">Login</button>
            </form>

            <p>
                Don't have an account?
                <Link to="/signup">Sign up</Link>
            </p>
        </div>
    );
}

export default LoginPage;