import { useState } from "react"
import {api} from "../services/api"
import { useNavigate } from "react-router-dom"

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
    <div style={{padding: "2rem", maxWidth: "400px", margin: "0 auto"}}>
      <p>Sign Up</p> 
      <form onSubmit={handleSubmit}>
        <input
          style={{width: "400px"}}
          name="first_name"
          type="text"
          placeholder="First Name"
          onChange={(e) => setFrist_name(e.target.value)}
          value={first_name}
        />
        <input
          style={{ width: "400px" }}
          name="last_name"
          type="text"
          placeholder="Last Name"
          onChange={(e) => setLast_name(e.target.value)}
          value={last_name}
        />
        <input
          style={{ width: "400px" }}
          name="email"
          type="text"
          placeholder="Email"
          onChange={(e) => setEmail(e.target.value)}
          value={email}
        />
        <input
          style={{ width: "400px" }}
          name="password"
          type="password"
          placeholder="Password"
          onChange={(e) => setPassword(e.target.value)}
          value={password}
        />
        <button type="submit">Sign Up</button>
        <p>Already have an account? <a href="/login">login</a></p>
        {error && <p>{error}</p>}
        {success && <p>{success}</p>}
      </form>
      

    </div>
  )
}

export default Register
