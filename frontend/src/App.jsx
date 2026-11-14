import { Route, Routes, Navigate } from "react-router";
import { useAuth } from "./hooks/useAuth";

import HomePage from "./pages/HomePage";
import LoginPage from "./pages/LoginPage";
import SignUpPage from "./pages/SignUpPage";

function App(){

    const {user,loading} = useAuth();

    
    if(loading){
        return <p>Checking session...</p>;
    }

    return(
        <Routes>
            <Route path="/"
                   element={user ? <HomePage/> : <Navigate to="/login" replace/>}
            />

            <Route path="/login"
                   element={user ? <Navigate to="/" replace/> : <LoginPage/>}
            />

            <Route path="/signup"
                   element={user ? <Navigate to="/" replace/> : <SignUpPage/>}
            />
        </Routes>
    );
}

export default App;
