import { useNavigate } from "react-router-dom"
import {useState, useEffect} from "react"
import { AuthContext } from "../../context/AuthContext"
import { useContext } from "react"
import SearchBar from "../searchBar/SearchBar"
import styles from "./Header.module.css"

export default function Header() {
    const [isMobile, setIsMobile] = useState(window.innerWidth <= 900)
    const navigate = useNavigate()
    const {user, logout} = useContext(AuthContext)

    function handleLogout () {
        logout()
        navigate("/")
    }

    useEffect(() => {
        const handleResize = () => {
            setIsMobile(window.innerWidth <=1024)
        }
        window.addEventListener("resize", handleResize)
        return () => window.removeEventListener("resize", handleResize)
    }, [])

    return (
        <>
            <header>
                <div>
                    <div className={styles.logo}>
                        <h1>MarkViz</h1>
                        <div className={styles.appName}>
                            <p>Market</p>
                            <p>Visualization</p>
                        </div>
                    </div>
                    <div className={styles.navParent}>
                        <SearchBar></SearchBar>
                        {!isMobile &&
                            <nav className={styles.nav}>
                                <div className={styles.navBtnParent}>
                                    <button className={styles.navBtn} onClick={() => navigate("/")}>
                                        Home
                                    </button>
                                    <button className={styles.navBtn} onClick={() => navigate("/portfolio")}>
                                        Portfolio
                                    </button>
                                    <button className={styles.navBtn} onClick={() => navigate("/trade")}>
                                        Trade
                                    </button>
                                </div>


                                {user ? (
                                    <button className={styles.primaryBtn} onClick={handleLogout}>
                                        Log Out
                                    </button>
                                ) : (
                                    <>
                                        <button className={styles.secondaryBtn} onClick={() => navigate("/login")}>
                                            Login
                                        </button>
                                        <button className={styles.primaryBtn} onClick={() => navigate("/register")}>
                                            Sign Up
                                        </button>
                                    </>
                                )}
                            </nav>
                        }
                        {
                            isMobile &&
                            <div className={styles.mobileAuth}>
                                {user ? <button className={styles.primaryBtn} onClick={handleLogout}>
                                    Log Out
                                </button>
                                    :
                                    <button className={styles.secondaryBtn} onClick={() => navigate("/login")}>
                                        Login
                                    </button>
                                }
                            </div>
                        }

                    </div>
                    <div className={styles.line}> </div>
                </div>
            </header>
            {
                isMobile &&
                (
                    <nav className={styles.bottomNav}>
                        <button className={styles.bottomNavBtn} onClick={() => navigate("/")}>
                            Home
                        </button>
                        <button className={styles.bottomNavBtn} onClick={() => navigate("/portfolio")}>
                            Portfolio
                        </button>
                        <button className={styles.bottomNavBtn} onClick={() => navigate("/trade")}>
                            Trade
                        </button>
                        <button className={styles.bottomNavBtn} onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}>
                            Search
                        </button>
                    </nav>
                )
            }
        </>
        
    )
}
