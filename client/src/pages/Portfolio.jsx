import { useState } from "react"
import Trade from "../components/Trade"

export default function Portfolio() {
    const [portfolioButton, setPortfolioButton] = useState(true)
    const [tradeButton, setTradeButton] = useState(false)

    const handlePortfolioClick = () => {
        setPortfolioButton(true)
        setTradeButton(false)
    }

    const handleTradeClick = () => {
        setTradeButton(true)
        setPortfolioButton(false)
    }

    return (
        <div>
            <button onClick={handlePortfolioClick}>Portfolio</button>
            <button onClick={handleTradeClick}>Trade</button>
            {
                portfolioButton &&
                <div style={{width: "400px", border: "solid black 5px"}}>Portfolio</div>
            }
            {
                tradeButton && 
                <div style={{ width: "400px", border: "solid green 5px" }}>
                    <Trade />
                </div>
            }
        </div>
    )
}

