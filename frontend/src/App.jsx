import { Route, Routes,Navigate } from "react-router";
import { useState, useEffect } from "react";

import {supabase} from "./config/supabase";
import LoginPage from "./pages/LoginPage";
import SignUpPage from "./pages/SignUpPage";
import HomePage from "./pages/HomePage";
function App() {

    const [session,setSession] = useState(null);

    const [checkingSession,SetCheckingSession] = useState(true);


    useEffect(()=>
        {
            const response = supabase.auth.onAuthStateChange(
              (event,newSession)=>{
                console.log("Auth event:",event);

                setSession(newSession);
                SetCheckingSession(false);
              });

              const subscription = response.data.subscription;

              return () => {
                    subscription.unsubscribe();
                };
            }
        ,[]);


     if(checkingSession){
        return <p>Checking session...</p>;
    }


    return (
        <Routes>

            <Route path="/login" element={<LoginPage />} />
            <Route path="/signup" element={session? <Navigate to="/" replace /> :<SignUpPage />} />
            <Route path="/" element={ <HomePage />} />
        </Routes>
    );
}

export default App;