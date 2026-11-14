
import { useState, useEffect } from "react";

import { supabase } from "../config/supabase";
import { AuthContext } from "./AuthContext";

function AuthProvider({children}){
    const [session,setSession] = useState(null);

    const [loading,setLoading] = useState(true);

    useEffect(() => {
        const {data: {subscription}} = supabase.auth.onAuthStateChange(
            (event,newSession) => {
                console.log("Auth event:",event);

                setSession(newSession);
                setLoading(false);
            }
        );

        return () => {
            subscription.unsubscribe();
        };
    }, []);

    const user = session?.user ?? null;

    const value = {
        session,
        user,
        loading
    };

    return(
        <AuthContext.Provider value={value}>
            {children}
        </AuthContext.Provider>
    );
}

export default AuthProvider;
