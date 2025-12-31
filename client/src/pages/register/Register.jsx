import { useState } from "react"
import {api} from "../../services/api"
import { useNavigate } from "react-router-dom"
import styles from "./Register.module.css"

function Register() {
  const [first_name, setFrist_name] = useState("")
  const [last_name, setLast_name] = useState("")
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState("")
  const [success, setSuccess] = useState("")

  const navigate = useNavigate()

  async function handleSubmit(e) {
    e.preventDefault()
    setError("")
    setSuccess("")
    
    try {
      await api.post("/auth/register", {first_name, last_name, email, password})
      setSuccess("Registeration Successful. Redirecting to Login ...")
      setTimeout(() => navigate("/login"), 2000)

    } catch (err) {
      console.log(err)
      setError(err.message || "Registration failed")
    }


  }
  return (
      <div className={styles.container}>
        <h1>Sign Up</h1>
      <form className={styles.form} onSubmit={handleSubmit}>
          <input
            className={styles.input}
            name="first_name"
            type="text"
            placeholder="First Name"
            onChange={(e) => setFrist_name(e.target.value)}
            value={first_name}
          />
          <input
            className={styles.input}
            name="last_name"
            type="text"
            placeholder="Last Name"
            onChange={(e) => setLast_name(e.target.value)}
            value={last_name}
          />
          <input
            className={styles.input}
            name="email"
            type="text"
            placeholder="Email"
            onChange={(e) => setEmail(e.target.value)}
            value={email}
          />
          <input
            className={styles.input}  
            name="password"
            type="password"
            placeholder="Password"
            onChange={(e) => setPassword(e.target.value)}
            value={password}
          />
          <button className={styles.signUpBtn} type="submit">Sign Up</button>
        </form>
        <p>Already have an account? <a className={styles.loginTag} href="/login">login</a></p>
        {error && <p>{error}</p>}
        {success && <p>{success}</p>}
      </div>
  )
}

export default Register
