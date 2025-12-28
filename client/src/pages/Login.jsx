import { useContext, useState } from "react";
import { useNavigate } from "react-router-dom";
import {api} from "../services/api";
import { AuthContext } from "../context/AuthContext";

export default function Login() {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");
    const { login } = useContext(AuthContext)
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError("");

        try {
            const data = await api.post("/auth/login", { email, password });
            localStorage.setItem("token", data.token); // Store token
            login(data.token)
            navigate("/portfolio"); // Redirect to home
        } catch (err) {
            setError(err.message || "Login failed");
        }
    };

    // localStorage.setItem("token", "eyJhbGciOiJIUzI1Ni...");  // Save JWT
    // const token = localStorage.getItem("token");             // Read it
    // localStorage.removeItem("token");                         // Delete it

    return (
        <div style={{ padding: "2rem", maxWidth: "400px", margin: "0 auto" }}>
            <h1>Login</h1>
            <form onSubmit={handleSubmit}>
                <input
                    type="email"
                    placeholder="Email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    style={{ display: "block", margin: "1rem 0", width: "100%" }}
                />
                <input
                    type="password"
                    placeholder="Password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                    style={{ display: "block", margin: "1rem 0", width: "100%" }}
                />
                <button type="submit">Login</button>
            </form>
            {error && <p style={{ color: "red" }}>{error}</p>}
            <p>
                No account? <a href="/register">Register</a>
            </p>
        </div>
    );
}
