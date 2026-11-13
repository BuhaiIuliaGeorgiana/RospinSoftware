import { Link } from "react-router";

function HomePage(){
    return(
        <div>
            <h1>Welcome to FloodLens!</h1>
            <Link to="/signup">Sign up</Link>
            <Link to="/login">Log in</Link>
        </div>
    )
}

export default HomePage;