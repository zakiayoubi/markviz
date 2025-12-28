import { useState, useEffect } from "react"
import {api} from "../services/api"

export default function QuickSummary({ ticker, onPriceLoad}) {
    const [summary, setSummary] = useState({})

    useEffect(() => {
        const fetchSummary = async () => {
            try {
                const response = await api.get(`/stocks/summary/${ticker}`)
                console.log(response)
                setSummary(response.data)
            } catch(err) {
                console.log("Error fetch the stock summary", err)
            }
        }
        fetchSummary()
    }, [])
    const {
        logo, stock_ticker, name, exchange,
        current_price, daily_change, percent_change,
        market_status, date,
        earnings_date, eps, market_cap, pe,
        volume, bid_ask, day_high, day_low,
        year_high, year_low
    } = summary

    useEffect(() => {
        if (onPriceLoad && current_price) {
            onPriceLoad(current_price)
        }
    }, [current_price, onPriceLoad])
    return (
        <div>
            <div>{logo}, {stock_ticker}, {name}, {exchange}</div>
            <div>
                <div>{current_price}, {daily_change}, {percent_change}</div>
                <div>{market_status} {date} </div>
            </div>
            <div>{earnings_date}, {eps}, {market_cap}, {pe}</div>
            <div>
                <table>
                    <tbody>
                        <tr>
                            <th>Volume</th>
                            <td>{volume}</td>
                            <th>Bid/Ask</th>
                            <td>{bid_ask}</td>
                        </tr>
                        <tr>
                            <th>Day's High</th>
                            <td>{day_high}</td>
                            <th>52 Week High</th>
                            <td>{year_high}</td>
                        </tr>
                        <tr>
                            <th>Day's Low</th>
                            <td>{day_low}</td>
                            <th>52 week Low</th>
                            <td>{year_low}</td>
                        </tr>
                    </tbody>
                    
                </table>
            </div>
        </div>
    )
}