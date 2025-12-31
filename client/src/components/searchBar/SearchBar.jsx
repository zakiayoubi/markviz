import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../../services/api";
import styles from "./SearchBar.module.css"

export default function SearchBar({onTickerSelect}) {
    const [allStocks, setAllStocks] = useState([])
    const [query, setQuery] = useState("")
    const [suggestions, setSuggestions] = useState([])
    const [showSuggestions, setShowSuggestions] = useState(false)
    const navigate = useNavigate()
    const inputRef = useRef(null)

    // fetch the stock tickers
    useEffect( () => {
        const fetchStocks = async() => {
            try{
            const response = await api.get("/stocks/all/tickers")
            setAllStocks(response.data)
            } catch (err) {
                console.log("Error loading the stock tickers: ", err)
            }
        }
        fetchStocks()
    }, [])

    // filter as user types
    useEffect(() => {
        if (query.trim() === "") {
            setSuggestions([])
            setShowSuggestions(false)
            return
        }
        const filtered = allStocks.filter(
            (stock) => 
                stock.ticker.toLowerCase().includes(query.toLowerCase()) ||
                stock.name.toLowerCase().includes(query.toLowerCase())
        ).slice(0, 8) // top 8 results
        setSuggestions(filtered)
        setShowSuggestions(true)
    }, [query, allStocks])

    const handleSelect = (ticker) => {
        setQuery("")
        setShowSuggestions(false)
        if (onTickerSelect) {
            onTickerSelect(ticker)
        } else {
            navigate(`/stock/${ticker}`)        
        }
    }

    useEffect(() => {
        const handleClickOutside = (e) => {
            if (inputRef.current && !inputRef.current.contains(e.target)) {
                setShowSuggestions(false)
            }
        }
        document.addEventListener("mousedown", handleClickOutside)
        return () => document.removeEventListener("mousedown", handleClickOutside)
    }, [])


    return (
        <div className={styles.container} ref={inputRef}>
            <input
            className={styles.input}
            type="text"
            placeholder="Search for stocks ..."
            value = {query}
            onChange={(e) => setQuery(e.target.value)}
            onFocus={() => query && setShowSuggestions(true)}
            />
            {showSuggestions && suggestions.length > 0 && (
                <div className={styles.suggestionCard}>
                    {suggestions.map((stock) => (
                        <div
                            className={styles.suggestion}
                            key={stock.ticker}
                            onClick={() => handleSelect(stock.ticker)}
                        >
                            <div className={styles.suggestionChild}>
                                <div className={styles.title}>
                                    <p className={styles.ticker}>{stock.ticker}</p>
                                    <p className={styles.companyName}>{stock.name}</p>
                                </div>
                                <p>{stock.exchange}</p>                              
                            </div>


                        </div>
                    ))}
                </div>
            )

            }
            
        </div>
    );
}