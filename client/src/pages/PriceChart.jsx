// src/components/PriceChart.jsx
import { Line } from 'react-chartjs-2';
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend,
    Filler
} from 'chart.js';
import { useEffect, useState } from 'react';
import {api} from "../services/api"
import { useParams } from 'react-router-dom';

// Simple vertical crosshair plugin (no dependencies!)
const crosshairPlugin = {
    id: 'crosshair',
    afterDraw: (chart) => {
        if (!chart.tooltip?._active?.length) return;

        const ctx = chart.ctx;
        const x = chart.tooltip.caretX;
        const topY = chart.chartArea.top;
        const bottomY = chart.chartArea.bottom;

        ctx.save();
        ctx.beginPath();
        ctx.moveTo(x, topY);
        ctx.lineTo(x, bottomY);
        ctx.lineWidth = 1;
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.6)';  // light white, visible on dark
        ctx.setLineDash([6, 6]);                       // dashed like Google Finance
        ctx.stroke();
        ctx.restore();
    }
};

// Register all needed components
ChartJS.register(
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend,
    Filler,
    crosshairPlugin
);


export default function PriceChart({ propTicker }) {
    const [timeRange, setTimeRange] = useState('1D')
    const [chartData, setChartData] = useState({labels: [], prices: []})
    const [loading, setLoading] = useState(true)
    const { paramTicker } = useParams()
    
    const ticker = paramTicker || propTicker
    
    useEffect(()=> {
        setChartData(true)
        const getChartData = async () => {
            try{
                const response = await api.get(`/stocks/${ticker}?range=${timeRange}`)
                const {labels, prices} = response.data
                setChartData({labels, prices})
            }
            catch (err) {
                console.log(err)
            }
            finally {
                setLoading(false)
            }
        }
        getChartData()
    }, [ticker, timeRange])

    const data = {
        labels: chartData.labels,
        datasets: [
            {
                label: 'Price ($)',
                data: chartData.prices,
                borderColor: '#2e7d32',        // green line
                backgroundColor: 'rgba(46, 125, 50, 0.2)', // light green fill
                fill: true,                    // area under the line
                tension: 0,                  // curves
                pointRadius: 0,                // hide points for clean look
                pointHoverRadius: 6,           // show on hover
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: '#2e7d32',
                pointHoverBorderWidth: 3
            }
        ]
    };

    const options = {
        responsive: true,
        maintainAspectRatio: false,
        interaction: {
            mode: 'index',        // ← THIS is the magic!
            intersect: false,     // ← Allows hover anywhere on the chart
        },
        plugins: {
            legend: { display: false },
            title: {
                display: true,
                text: 'AAPL - Price (Last 30 Days)',
                font: { size: 18 },
                color: '#fff'
            },
            
            tooltip: {
                backgroundColor: 'rgba(0, 0, 0, 0.8)',
                titleColor: '#fff',
                bodyColor: '#fff',
                cornerRadius: 8,
                displayColors: false,               // hide the little color box
                callbacks: {
                    label: function (context) {
                        return `Price: $${context.parsed.y.toFixed(2)}`;
                    }
                }
            }
        },
        scales: {
            x: {
                grid: { display: false },
                ticks: {
                    color: '#aaa',
                    maxTicksLimit: 6, // General limit
                    // // Show label only every Nth point
                    // callback: function (value, index, ticks) {
                    //     // For 1D: show every ~1 hours (assuming ~390 points in a day)
                    //     if (timeRange === '1D') {
                    //         return (index  % 90) === 0 ? this.getLabelForValue(value) : '';
                    //     }
                    //     // For other ranges: show every 5th or so
                    //     // return index % Math.ceil(ticks.length / 4) === 0 ? this.getLabelForValue(value) : '';
                    // }
                }
            },
            y: {
                grid: { display: false },
                ticks: { color: '#aaa' }
            }
        }
    };

    return (
        <div>
            <div style={{ marginBottom: '10px', textAlign: 'center' }}>
                {['1D', '1W', '1M', '3M', '6M', 'YTD', '1Y', '5Y', 'MAX'].map((range) => (
                    <button
                        key={range}
                        onClick={() => setTimeRange(range)}
                        style={{
                            padding: '8px 12px',
                            margin: '0 4px',
                            backgroundColor: timeRange === range ? '#2e7d32' : '#333',
                            color: 'white',
                            border: 'none',
                            borderRadius: '4px',
                            cursor: 'pointer',
                            fontSize: '14px',
                        }}
                    >
                        {range}
                    </button>
                ))}
            </div>
            <div style={{ height: '400px', padding: '20px' }}>
                <Line data={data} options={options} />
            </div> 
        </div>

        
    );
}