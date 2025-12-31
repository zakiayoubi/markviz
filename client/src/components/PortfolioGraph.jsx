import {useState, useEffect} from "react"
import {LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend} from "recharts"
import {api} from "../services/api"

export default function PortfolioGraph () {
    const [timeRange, setTimeRange] = useState("1D")
    const [loading, setLoading] = useState(false)
    const [data, setData] = useState([])

    useEffect(() => {
        const fetchPerformance = async () => {
            setLoading(true)
            try {
                const response = await api.get(`/portfolio/graph?timeRange=${timeRange}`)
                console.log(response.data)
                setData(response.data)
                setLoading(false)
            } catch(err) {
                console.log(err)
            }
        }
        fetchPerformance()
    }, [timeRange])

    // const data = [
    //     { date: '2024-01', value: 10000 },
    //     { date: '2024-02', value: 10500 },
    //     { date: '2024-03', value: 10200 },
    //     { date: '2024-04', value: 11000 },
    //     { date: '2024-05', value: 11500 },
    //     { date: '2024-06', value: 12000 },
    // ]
        
    
    const timeRanges = ['1D', '1W', '1M', '3M', '1Y', 'ALL']
    return (
        <div>
            <h2>Portfolio Performance</h2>
            <div>
                {timeRanges.map((range) => (
                    <button
                        key={range}
                        onClick={() => setTimeRange(range)}
                        style={{
                            padding: '8px 16px',
                            marginRight: '8px',
                            backgroundColor: timeRange === range ? '#00c853' : '#e0e0e0',
                            color: timeRange === range ? 'white' : 'black',
                            border: 'none',
                            borderRadius: '4px',
                            cursor: 'pointer',
                            fontWeight: timeRange === range ? 'bold' : 'normal',
                        }}
                        >
                        {range}
                    </button>
                ))}
            </div>
            {loading ? (<div> Loading ... </div>) : (
                <LineChart width={600} height={300} data={data}>
                    <CartesianGrid strokeDasharray="3 3"/>
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line 
                        type="monotone"
                        dataKey="value"
                        stroke="#8884d8"
                        strokeWidth={2}
                        dot={false}
                    />
                </LineChart>
            )}
        </div>
    )
}