import { useNavigate } from "react-router-dom"
import { AuthContext } from "../context/AuthContext"
import { useContext } from "react"
import SearchBar from "../components/SearchBar"
export default function Header() {

    const navigate = useNavigate()
    const {user, logout} = useContext(AuthContext)
    function handleLogout () {
        logout()
        navigate("/")
    }
    return (
        <header>
            <div>
                <SearchBar></SearchBar>
                <button onClick={() => navigate("/portfolio")}>Portfolio</button>
                <button onClick={() => navigate("/login")}> Login</button>
                <button onClick={() => navigate("/register")}>Sign Up</button>
                {user && <button onClick={handleLogout}> Log Out</button>}
            </div>
        </header>
    )
}

// what do I want:
// 1. a search bar
// 2. on typing the search bar should suggest stock tickers in a new panel
// a. create a list of all stocks of nyse and nasdaq
// b. or should I just cache it in my server and update it every 24 hours or 
// every morning at 6am depending on timezone
// c
// 3. onClick it should refer you to the stock/ticker page.
