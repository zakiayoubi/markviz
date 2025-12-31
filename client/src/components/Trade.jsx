import { useState } from "react"
import SearchBar from "./searchBar/SearchBar"
import PriceChart from "./PriceChart"
import QuickSummary from "./QuickSummary"
import {api} from "../services/api"

export default function Trade({ onSuccess }) {
    const [selectedTicker, setSelectedTicker] = useState(null)

    const [action, setAction] = useState("buy")
    const [quantity, setQuantity] = useState(0)
    const [orderType, setOrderType] = useState("market")
    const [duration, setDuration] = useState("day")

    const [currentPrice, setCurrentPrice] = useState(null)


    const handleSubmit = async (e) => {
        e.preventDefault()
        try {
           const data = {
            "ticker": selectedTicker,
            "shares": quantity,
            "buy_price": currentPrice
            }
            const response = await api.post("/portfolio/holdings", data)
            console.log(response)
            if (response.status === 200) {
                onSuccess()
            } 
        } catch (err) {
            console.log(err)
        }
        

    }

    return (
        <div style={{ width: "400px", border: "solid green 5px" }}>Trade
            <SearchBar onTickerSelect={setSelectedTicker}></SearchBar>
            {selectedTicker &&
                <div>
                    <PriceChart propTicker={selectedTicker}></PriceChart>
                    <QuickSummary ticker={selectedTicker} onPriceLoad={setCurrentPrice}></QuickSummary>
                </div>
            }
            <div>
                <form onSubmit={handleSubmit}>
                    <label htmlFor="action">Action</label>
                    <select 
                    value={action}
                    onChange={(e) => setAction(e.target.value)}
                    id="action">
                        <option value="buy">Buy</option>
                        <option value="sell">Sell</option>
                        <option value="shortSell" disabled>Short Sell (coming soon)</option>
                        <option value="buyToCcover" disabled>Buy to cover (coming soon)</option>
                    </select>

                    <label htmlFor="quantity">Quantity</label>
                    <input
                    type="number"
                    name="quantity"
                    value={quantity}
                    onChange={(e) => setQuantity(e.target.value)}
                    id="quantity"/>

                    <label htmlFor="orderType">Order Type</label>
                    <select 
                    value={orderType}
                    onChange={(e) => setOrderType(e.target.value)}
                    id="orderType">
                        <option value="market">Market</option>
                        <option value="limit (coming soon)" disabled>Limit (coming soon)</option>
                        <option value="stopLimit (coming soon)" disabled>Stop Limit (coming soon)</option>
                    </select>

                    <label htmlFor="duration">Duration</label>
                    <select 
                    value={duration}
                    onChange={(e) => setDuration(e.target.value)}
                    id="duration">
                        <option value="dayOnly">Day Only</option>
                        <option value="goodUntilCancelled (coming soon)" disabled>Good until cancelled (coming soon)</option>
                    </select>
                    <button 
                    type="submit" 
                    disabled={!selectedTicker}
                    title={!selectedTicker ? "Select a stock first": ""}
                    > PLACE ORDER</button>
                </form>
            </div>  
        </div>
    )
}

