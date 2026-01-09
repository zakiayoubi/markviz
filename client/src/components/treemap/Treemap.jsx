import { useEffect, useRef, useState } from 'react';
import {api} from "../../services/api"
import * as d3 from 'd3';
import { useNavigate } from 'react-router-dom';
import styles from "./Treemap.module.css"

const colorScale = d3.scaleLinear()
    .domain([-15, -10, -7.5, -5, -2.5, 0, 2.5, 5, 7.5, 10, 15])
    .range([
        '#b71c1c', // dark red (strong negative)
        '#c62828', // red
        '#d32f2f', // medium-dark red
        '#e53935', // medium red
        '#ef5350', // light red
        '#424242', // dark gray (near zero)
        '#66bb6a', // light green
        '#43a047', // medium green
        '#2e7d32', // green
        '#1b5e20', // dark green
        '#0d4710'  // very dark green (strong positive)
    ])
    .interpolate(d3.interpolateRgb);

export default function Treemap() {
    const svgRef = useRef(null);
    const [data, setData] = useState(null);
    const navigate = useNavigate()

    useEffect(() => {
        const loadData = async () => {
            try {
                const rawData = (await api.get("/stocks/sp500")).data;
                console.log(rawData)
                const grouped = d3.group(rawData, d => d.sector);
                const rootNode = {
                    id: "Root",
                    children: Array.from(grouped, ([sector, companies]) => ({
                        id: sector,
                        children: companies.map(c => ({
                            id: c.ticker,
                            value: c.market_cap,
                            percentChange: c.change_percent
                        }))
                    }))
                };
                const hierarchy = d3.hierarchy(rootNode)
                    .sum(d => d.value || 0);
                
                setData(hierarchy);
            } catch (error) {
                console.error('Error loading data:', error);
            }
        };

        loadData();
    }, []);

    // Drawing function
    const drawTreemap = () => {
        if (!data || !svgRef.current) return;

        const svg = d3.select(svgRef.current);
        svg.selectAll('*').remove();

        const width = svgRef.current.clientWidth;
        const height = svgRef.current.clientHeight;

        const treemap = d3.treemap()
            .size([width, height])
            .paddingOuter(8)
            .paddingInner(1)
            .round(true);

        const root = treemap(data);

        // Company rectangles
        const cells = svg
            .selectAll('g.cell')
            .data(root.leaves())
            .join('g')
            .attr('class', 'cell');

        cells
            .append('rect')
            .attr('x', d => d.x0)
            .attr('y', d => d.y0)
            .attr('width', d => d.x1 - d.x0)
            .attr('height', d => d.y1 - d.y0)
            .attr('fill', d => colorScale(d.data.percentChange))
            .attr('stroke', '#fff')
            .attr('stroke-width', 1);

        // Company names 
        cells
            .append('text')
            .attr('x', d => (d.x0 + d.x1) / 2)
            .attr('y', d => (d.y0 + d.y1) / 2)
            .attr('dy', '0.35em')
            .attr('text-anchor', 'middle')
            .attr('font-size', d => Math.min(18, (d.x1 - d.x0) / 4))
            .attr('font-weight', '600')
            .attr('fill', 'white')
            .style('pointer-events', 'none')
            .text(d => ((d.x1 - d.x0) > 30 && (d.y1 - d.y0) > 20)? d.data.id : '');
        
        // Percent Change
        cells
            .append('text')
            .attr('x', d => (d.x0 + d.x1) / 2)
            .attr('y', d => (d.y0 + d.y1) / 2 + 20)
            .attr('dy', '0.35em')
            .attr('text-anchor', 'middle')
            .attr('font-size', d => Math.min(14, (d.x1 - d.x0) / 4))
            .attr('font-weight', '400')
            .attr('fill', 'white')
            .style('pointer-events', 'none')
            .text(d => {
                const width = d.x1 - d.x0;
                const height = d.y1 - d.y0;
                // Show only if there's enough space (width OR height > threshold)
                return (width > 40 && height > 50) ? `${d.data.percentChange > 0 ? '+' : ''}${d.data.percentChange}%` : '';
            });

        // Sector labels
        const sectorGroups = svg
            .selectAll('g.sector-label')
            .data(root.descendants().filter(d => d.depth === 1))
            .join('g')
            .attr('class', 'sector-label');

        sectorGroups
            .append('text')
            .attr('x', d => (d.x0 + d.x1) / 2)
            .attr('y', d => d.y0 + 4)
            .attr('text-anchor', 'middle')
            .attr('font-size', 14)
            .attr('font-weight', '800')
            .attr('fill', '#ffffffff')
            .text(d => d.data.id);

        // Add hover behavior to the entire cell group
        cells
            .on('mousemove', function (event, d) {
                const tooltip = d3.select('#treemap-tooltip');

                // Update tooltip content
                tooltip
                    .html(`
        <strong>${d.data.id}</strong><br/>
        Change: ${d.data.percentChange > 0 ? '+' : ''}${d.data.percentChange.toFixed(2)}%<br/>
        Market Cap: ${(d.value / 1e9).toFixed(2)}B USD
      `);

                // Position tooltip near mouse (with offset so it doesn't cover the rectangle)
                tooltip
                    .style('left', (event.pageX - 50) + 'px')
                    .style('top', (event.pageY - 200) + 'px')
                    .style('opacity', 1); // make visible
            })
            .on('mouseout', function () {
                d3.select('#treemap-tooltip')
                    .style('opacity', 0); // hide again
            });

        // onclick
        cells
            .style('cursor', 'pointer')  // shows hand cursor on hover
            .on('click', function (event, d) {
                console.log(d.data.id)
                navigate(`/stock/${d.data.id}`);

            });
    };

    // Run drawing when data loads, and on resize
    useEffect(() => {
        drawTreemap();

        const handleResize = () => {
            drawTreemap();
        };

        window.addEventListener('resize', handleResize);

        return () => {
            window.removeEventListener('resize', handleResize);
        };
    }, [data]); // Only re-run when data changes

    return (
        <div className={styles.container}>
            <svg ref={svgRef} className={styles.svg}/>
            <div
                id="treemap-tooltip"
                className={styles.tooltip}
            />
        </div>
    );
}