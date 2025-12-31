import { useEffect, useState } from "react"
import {api} from "../services/api"

export default function PortfolioTable() {
    const [positions, setPositions] = useState([])
    const [loading, setLoading] = useState(false)
    useEffect(() => {
        setLoading(true)
        const fetchPortfolioTable = async () => {
            try {
                const response = await api.get("/portfolio/table")
                console.log(response)
                setPositions(response.data)
            } catch (err) {
                console.log(err)
            } finally {
                setLoading(false)
            }
        }
        fetchPortfolioTable()
    }, [])
    { loading && <div>Loading ...</div> }
    return (
        <div>
            <div style={{ display: "flex", flexDirection: "row" }}>
                <div style={{ width: "8rem" }}>Position</div>
                <div style={{ width: "8rem" }}>Total Value</div>
                <div style={{ width: "8rem" }}>Today Price</div>
                <div style={{ width: "8rem" }}>All Time Return</div>
            </div>
            <div>
                {positions.map((position) => (
                    <div style={{ display: "flex", flexDirection: "row", gap: "5rem" }}>
                        <div style={{display: "flex", flexDirection: "column", width: "50px"}}>
                            <div>{position.ticker}</div>
                            <div>{position.name}</div>                            
                        </div>
                        <div style={{ display: "flex", flexDirection: "column", width: "50px" }}>
                            <div>{position.totalValue}</div>
                            <div>{position.shares}</div>
                        </div>
                        <div style={{ display: "flex", flexDirection: "column", width: "50px" }}>
                            <div>{position.currentPrice}</div>
                            <div>{position.todayChangePercent}</div>
                        </div>
                        <div style={{ display: "flex", flexDirection: "column", width: "50px" }}>
                            <div>{position.allTimeReturnAmount}</div>
                            <div>{position.allTimeReturn}</div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    )
}