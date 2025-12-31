import { useState, useEffect } from "react";
import { api } from "../services/api";
import { useParams } from "react-router-dom";

export default function StockStats() {
    const [stats, setStats] = useState(null);
    const [loading, setLoading] = useState(true);
    const { ticker } = useParams()

    useEffect(() => {
        const fetchStats = async () => {
            try {
                const res = await api.get(`/stocks/stats/${ticker}`);
                setStats(res.data);
            } catch (err) {
                console.error(err);
            } finally {
                setLoading(false);
            }
        };
        fetchStats();
    }, [ticker]);

    if (loading) return <div style={{ padding: "2rem" }}>Loading stats...</div>;
    if (!stats) return <div style={{ padding: "2rem" }}>No stats available</div>;

    const { valuation, performance, financial_health, trading_activity } = stats;

    const StatGroup = ({ title, items }) => (
        <div style={{ marginBottom: "2rem" }}>
            <h3 style={{ margin: "0 0 1rem 0", color: "#aaa", fontSize: "1.1rem" }}>{title}</h3>
            <table style={{ width: "100%", borderCollapse: "separate", borderSpacing: "0 8px" }}>
                <tbody>
                    {items.map(([key, value]) => (
                        <tr key={key}>
                            <td style={{ color: "#aaa", paddingRight: "2rem" }}>{key}</td>
                            <td style={{ textAlign: "right", fontWeight: "600" }}>{value}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );

    return (
        <div style={{ padding: "2rem" }}>
            <h2 style={{ marginBottom: "2rem" }}>Key Statistics</h2>
            <div style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
                gap: "2rem"
            }}>
                <StatGroup
                    title="Valuation"
                    items={[
                        ["Market Cap", valuation.market_cap],
                        ["P/E Ratio", valuation.pe_ratio !== "N/A" ? valuation.pe_ratio.toFixed(2) : "N/A"],
                        ["Forward P/E", valuation.forward_pe !== "N/A" ? valuation.forward_pe.toFixed(2) : "N/A"],
                        ["Price/Sales", valuation.price_to_sales !== "N/A" ? valuation.price_to_sales.toFixed(2) : "N/A"],
                        ["Price/Book", valuation.price_to_book !== "N/A" ? valuation.price_to_book.toFixed(2) : "N/A"],
                    ]}
                />
                <StatGroup
                    title="Performance"
                    items={[
                        ["Today", `${performance.change_today_percent > 0 ? "+" : ""}${performance.change_today_percent?.toFixed(2)}%`],
                        ["52W High", `$${performance.fifty_two_week_high?.toFixed(2)}`],
                        ["52W Low", `$${performance.fifty_two_week_low?.toFixed(2)}`],
                        ["YTD Return", performance.ytd_return !== "N/A" ? `${performance.ytd_return?.toFixed(2)}%` : "N/A"],
                        ["1Y Return", performance.one_year_return !== "N/A" ? `${(performance.one_year_return * 100).toFixed(2)}%` : "N/A"],
                    ]}
                />
                <StatGroup
                    title="Financial Health"
                    items={[
                        ["Debt/Equity", financial_health.debt_to_equity !== "N/A" ? financial_health.debt_to_equity.toFixed(2) : "N/A"],
                        ["Current Ratio", financial_health.current_ratio !== "N/A" ? financial_health.current_ratio.toFixed(2) : "N/A"],
                        ["Profit Margin", financial_health.profit_margin !== "N/A" ? `${(financial_health.profit_margin * 100).toFixed(2)}%` : "N/A"],
                        ["ROE", financial_health.roe !== "N/A" ? `${(financial_health.roe * 100).toFixed(2)}%` : "N/A"],
                    ]}
                />
                <StatGroup
                    title="Trading Activity"
                    items={[
                        ["Volume Today", trading_activity.volume_today?.toLocaleString() || "N/A"],
                        ["Avg Volume (3M)", trading_activity.avg_volume?.toLocaleString() || "N/A"],
                        ["Beta", trading_activity.beta !== "N/A" ? trading_activity.beta.toFixed(2) : "N/A"],
                        ["Shares Outstanding", trading_activity.shares_outstanding?.toLocaleString() || "N/A"],
                        ["Float", trading_activity.float?.toLocaleString() || "N/A"],
                    ]}
                />
            </div>
        </div>
    );
}