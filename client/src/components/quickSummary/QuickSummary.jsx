import { useState, useEffect } from "react"
import {api} from "../../services/api"
import styles from "./QuickSummary.module.css"

export default function QuickSummary({ ticker, onPriceLoad}) {
    const [summary, setSummary] = useState({})

    useEffect(() => {
        const fetchSummary = async () => {
            try {
                const response = await api.get(`/stocks/summary/${ticker}`)
                setSummary(response.data)
            } catch(err) {
                console.log("Error fetch the stock summary", err)
            }
        }
        fetchSummary()
    }, [])

    const get_date = () => {
        const date = new Date()
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: 'numeric',
            minute: '2-digit',
            timeZoneName: 'short'
        })
    }

    const convertEarningsDate = (isoDate) => {
        const date = new Date(isoDate)
        return date.toLocaleString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
        })
    }
    const {
        current_price,
        market_status,
        earnings_date, eps, market_cap, pe,
        volume, bid_ask, day_high, day_low,
        year_high, year_low
    } = summary

    useEffect(() => {
        if (onPriceLoad && current_price) {
            onPriceLoad(current_price)
        }
    }, [current_price])

    return (
        <div className={styles.container}>
                <div className={styles.header}>
                    <h2>Stock Detail</h2>
                    <div>
                        <p>{get_date()}</p> 
                        <p>Market: <span> {market_status}</span></p>
                    </div>
                </div>

                <table className={styles.stockDetail}> 
                    <tbody>
                        <tr className={styles.stockDetailRow}>
                            <th>Earning's Date</th>
                            <td>{convertEarningsDate(earnings_date)}</td>
                        </tr>
                        <tr>
                            <th>EPS</th>
                            <td>{eps}</td>                            
                        </tr>
                        <tr>
                            <th>PE</th>
                            <td>{pe}</td>                            
                        </tr>
                        <tr>
                            <th>Market Cap</th>
                            <td>{market_cap}</td>                            
                        </tr>
                        <tr>
                            <th>Bid/Ask</th>
                            <td>${bid_ask}</td>
                        </tr>
                        <tr>
                            <th>Volume</th>
                            <td>{volume}</td>
                        </tr>
                        <tr>
                            <th>Day's High</th>
                            <td>{day_high}</td>
                        </tr>

                        <tr>
                            <th>Day's Low</th>
                            <td>{day_low}</td>
                        </tr>
                        <tr>
                            <th>52 Week High</th>
                            <td>{year_high}</td>
                        </tr>

                        <tr>
                            <th>52 Week Low</th>
                            <td>{year_low}</td>
                        </tr>
                    </tbody>
                </table>
            </div>
    )
}