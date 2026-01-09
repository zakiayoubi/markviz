
import { useEffect, useState } from 'react';
import {api} from "../../services/api"
import { useParams } from 'react-router-dom';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts"
import styles from "./PriceChart.module.css"


export default function PriceChart({ propTicker }) {
    const [detail, setDetail] = useState({})
    const [timeRange, setTimeRange] = useState('1D')
    const [data, setData] = useState([])
    const [loading, setLoading] = useState(false)
    const { ticker } = useParams()
    
    const stockTicker = ticker || propTicker

    const date = () => {
        const date = new Date()

        return date.toLocaleString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: 'numeric',
            minute: '2-digit',
            timeZoneName: 'short'
        })
    }
    
    useEffect(()=> {
        const getChartData = async () => {
            setLoading(true)
            try{
                const response = await api.get(`/stocks/${stockTicker}?timeRange=${timeRange}`)
                setDetail(response.stockDetail)
                setData(response.data)
            }
            catch (err) {
                console.log(err)
            }
            finally {
                setLoading(false)
            }
        }
        getChartData()
    }, [stockTicker, timeRange])

    const getLineColor = () => {
        if (!data || data.length < 2) return 'var(--gain)'
        const firstPrice = data[0].price
        const lastPrice = data[data.length - 1].price
        return lastPrice >= firstPrice ? 'var(--gain)' : 'var(--loss)'
    }

    const timeRanges = ['1D', '1W', '1M', '3M', '6M', 'YTD', '1Y', '5Y', 'ALL']
    return (
        <div className={styles.container}>
            <div className={styles.detail}>
                <div className={styles.titleContainer}>
                    <h2>{detail.name}</h2>
                    <p>{detail.exchange} : <span>{stockTicker}</span></p>                    
                </div>

                <h1>{detail.currentPrice} <span className={styles.currency}>USD</span></h1>
                <div
                    className={`${styles.dailyReturn} ${detail.dollarChange > 0 ? styles.gain : styles.loss}`}
                    >
                    <p>${detail.dollarChange}</p>
                    <p>{detail.percentChange}% today</p>                                     
                </div>
                <p>{date()}</p>  

            </div>
            <div className={styles.rangeContainer}>
                {timeRanges.map((range) => (
                    <button
                        className={`${styles.timeRangeBtn} ${timeRange === range ? styles.active : ''}`}
                        key={range}
                        onClick={() => setTimeRange(range)}
                        
                    >
                        {range}
                    </button>
                ))}
            </div>
            {loading ? (<div> Loading ... </div>) : (
                <div className={styles.graphContainer}>
                    <ResponsiveContainer width="100%" height={400}>
                        <LineChart data={data}>
                            {/* <CartesianGrid strokeDasharray="3 3" /> */}
                            <XAxis
                                dataKey="date"
                                interval={Math.floor(data.length / 5) - 1}
                            />
                            <YAxis
                                domain={['auto', 'auto']}
                                tickFormatter={(value) => value.toFixed(1)}
                            />
                            <Tooltip
                                contentStyle={{
                                    backgroundColor: 'var(--bg-secondary)',
                                    border: '1px solid var(--border)',
                                    borderRadius: '8px',
                                    color: 'var(--text-primary)',
                                    padding: '12px'
                                }}
                                labelStyle={{
                                    color: 'var(--text-secondary)',
                                    marginBottom: '4px',

                                }}
                                itemStyle={{
                                    color: 'var(--text-secondary)',
                                    padding: '4px 0',
                                    fontWeight: 'bold'

                                }}
                                formatter={(value) => `$${value.toFixed(2)}`}
                            />
                            <Line
                                type="monotone"
                                dataKey="price"
                                stroke={getLineColor()}
                                strokeWidth={2}
                                dot={false}
                            />
                        </LineChart> 
                    </ResponsiveContainer>
                   
                </div>
                
            )}
        </div>
    )
}