import { Route, Routes } from "react-router";


import LoginPage from "./pages/LoginPage";
import SignUpPage from "./pages/SignUpPage";
import HomePage from "./pages/HomePage";
function App() {
    return (
        <Routes>

            <Route path="/login" element={<LoginPage />} />
            <Route path="/signup" element={<SignUpPage />} />
            <Route path="/" element={<HomePage />} />
        </Routes>
    );
}

export default App;