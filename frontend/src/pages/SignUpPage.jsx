import { Link } from "react-router";
function SignUpPage(){
    return(
        <div>
            <h1>Welcome</h1>
            <form>
                <label htmlFor="email">Email:</label>
                <input id ="email" type ="email" />

                <label htmlFor="password">Password:</label>
                <input id ="password" type ="password" />

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