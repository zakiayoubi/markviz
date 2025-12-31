import { useContext, useState } from "react";
import { useNavigate } from "react-router-dom";
import {api} from "../../services/api";
import { AuthContext } from "../../context/AuthContext";
import styles from "./Login.module.css"

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
        <div className={styles.container}>
            <h1>Login</h1>
            <form className={styles.form} onSubmit={handleSubmit}>
                <input
                    className={styles.input}
                    type="email"
                    placeholder="Email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                />
                <input
                    className={styles.input}
                    type="password"
                    placeholder="Password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    required
                />
                <button className={styles.loginBtn} type="submit">Login</button>
            </form>
            {error && <p style={{ color: "red" }}>{error}</p>}
            <p>
                Don't have an account? <a className={styles.registerTag}href="/register">Sign up</a>
            </p>
        </div>
    );
}
