import { supabase } from "../config/supabase";

export async function register(email,password){
    return await supabase.auth.signUp({
        email:email,
        password:password
    });
}

export async function login(email,password){
    return await supabase.auth.signInWithPassword({
        email:email,
        password:password
    });
}

export async function logout(){
    return await supabase.auth.signOut();
}