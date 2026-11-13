import { Link } from "react-router";
import {useState} from "react";
function SignUpPage(){
    const [email,setEmail] = useState("");
    const [password,setPassword] = useState("");
    const [confirmPassword,setConfirmPassword] = useState("");
    const [error,setError] = useState("");
    function handleSignUp(event){
        event.preventDefault();
        if(password === confirmPassword){
            console.log("Email:", email);
            console.log("Login form submitted");
            setError("");
        }else{
            setError("password and confirm password do not match!");
            return;
        }
    }
    return(
        <div>
            <h1>Welcome</h1>
            <form onSubmit={handleSignUp}>
                <label htmlFor="email">Email:</label>
                <input  id ="email" 
                        type ="email" 
                        value = {email}
                        onChange = {(e)=> setEmail(e.target.value)}
                        required
                        />

                <label htmlFor="password">Password:</label>
                <input id ="password" 
                        type ="password" 
                        value = {password}
                        onChange = {(e)=> setPassword(e.target.value)}
                        required
                        />

                <label htmlFor="confirmPassword">Password:</label>
                <input id ="confirmPassword" 
                        type ="password" 
                        value = {confirmPassword}
                        onChange = {(e)=> setConfirmPassword(e.target.value)}
                        required
                        />

                {error && <p role = "alert">{error}</p>}

                <button type = "submit">Sign up</button>
            </form>

            <p>
                Already have an account?
                <Link to="/login">Log in</Link>
            </p>
        </div>
    );
}

export default SignUpPage;