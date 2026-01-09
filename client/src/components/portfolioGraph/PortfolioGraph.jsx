import {useState, useEffect} from "react"
import {LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer} from "recharts"
import {api} from "../../services/api"
import styles from "./PortfolioGraph.module.css"

export default function PortfolioGraph () {
    const [timeRange, setTimeRange] = useState("1D")
    const [loading, setLoading] = useState(false)
    const [data, setData] = useState([])

    useEffect(() => {
        const fetchPerformance = async () => {
            setLoading(true)
            try {
                const response = await api.get(`/portfolio/graph?timeRange=${timeRange}`)
                setData(response.data)
            } catch(err) {
                console.log(err)
            } finally {
                setLoading(false)
            }
        }
        fetchPerformance()
    }, [timeRange])

    const getLineColor = () => {
        if (!data || data.length < 2) return 'var(--gain)'
        const firstPrice = data[0].value
        const lastPrice = data[data.length - 1].value
        return lastPrice >= firstPrice ? 'var(--gain)' : 'var(--loss)'
    }

    const timeRanges = ['1D', '1W', '1M', '3M', '1Y', 'ALL']
    return (
        <div>
            <h2 className={styles.title}>Portfolio Performance</h2>
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
                                formatter={(value) => `%${value.toFixed(2)}`}
                            />
                            <Line
                                type="monotone"
                                dataKey="value"
                                name="Return"
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