import { useEffect, useState } from "react"
import {api} from "../../services/api"
import styles from "./PortfolioTable.module.css"

export default function PortfolioTable() {
    const [positions, setPositions] = useState([])
    const [loading, setLoading] = useState(false)
    const [isMobile, setIsMobile] = useState(false)
    const [selectedView, setSelectedView] = useState('allTimeReturn');

    useEffect(() => {
        setLoading(true)
        const fetchPortfolioTable = async () => {
            try {
                const response = await api.get("/portfolio/table")
                setPositions(response.data)
            } catch (err) {
                console.log(err)
            } finally {
                setLoading(false)
            }
        }
        fetchPortfolioTable()
    }, [])

    useEffect(() => {
        const handleResize = () => {
            setIsMobile(window.innerWidth <= 768)
        }
        window.addEventListener("resize", handleResize)
        return () => window.removeEventListener("resize", handleResize)
    }, [])

    { loading && <div>Loading ...</div> }
    return (
        <div>
            {!isMobile && 
                <div className={styles.container}>
                    <div className={styles.headerSection}>
                        <p>Position</p>
                        <div className={styles.headerDetail}>
                            <p>Total Value</p>
                            <p>Today Price</p>
                            <p>All Time Return</p>
                        </div>
                    </div>
                    <div className={styles.positionContainer}>
                        {positions.map((position) => (
                            <div
                                className={styles.position}
                                key={position.ticker}
                            >
                                <div className={styles.positionName}>
                                    <p>{position.ticker}</p>
                                    <p>{position.name}</p>
                                </div>
                                <div className={styles.positionDetail}>
                                    <div>
                                        <p>{position.totalValue} USD</p>
                                        <p>{position.shares} shares</p>
                                    </div>
                                    <div>
                                        <p>{position.currentPrice} USD</p>
                                        <p className={`${position.todayChangePercent > 0 ? styles.gain : styles.loss}`}>{position.todayChangePercent}%</p>
                                    </div>
                                    <div>
                                        <p className={`${position.allTimeReturnAmount > 0 ? styles.gain : styles.loss}`}>{position.allTimeReturnAmount} USD</p>
                                        <p className={`${position.allTimeReturn > 0 ? styles.gain : styles.loss}`}>{position.allTimeReturn}%</p>
                                    </div>
                                </div>

                            </div>
                        ))}
                    </div>
                </div>
            }
            {isMobile &&
                <div className={styles.container}>
                    <div className={styles.headerSection}>
                        <p>Position</p>
                        <select
                            value={selectedView} onChange={(e) => setSelectedView(e.target.value)}>
                            <option value="allTimeReturn">All Time Return</option>
                            <option value="totalValue">Total Value</option>
                            <option value="todayPrice">Today Price</option>
                        </select>
                    </div>
                    <div className={styles.positionContainer}>
                        {positions.map((position) => (
                            <div
                                className={styles.position}
                                key={position.ticker}
                            >
                                <div className={styles.positionName}>
                                    <p>{position.ticker}</p>
                                    <p>{position.name}</p>
                                </div>
                                <div className={styles.positionDetail}>
                                    {selectedView === "totalValue" &&
                                        <div>
                                            <p>{position.totalValue} USD</p>
                                            <p>{position.shares} shares</p>
                                        </div>
                                    }
                                    {selectedView === "todayPrice" &&
                                        <div>
                                            <p>{position.currentPrice} USD</p>
                                            <p className={`${position.todayChangePercent > 0 ? styles.gain : styles.loss}`}>{position.todayChangePercent}%</p>
                                        </div>
                                    }
                                    {selectedView === "allTimeReturn" && 
                                        <div>
                                            <p className={`${position.allTimeReturnAmount > 0 ? styles.gain : styles.loss}`}>{position.allTimeReturnAmount} USD</p>
                                            <p className={`${position.allTimeReturn > 0 ? styles.gain : styles.loss}`}>{position.allTimeReturn}%</p>
                                        </div>
                                    }
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            }
        </div>
        
        
    )
}