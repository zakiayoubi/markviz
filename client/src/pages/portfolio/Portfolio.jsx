import { useState } from "react"
import PortfolioTable from "../../components/portfolioTable/PortfolioTable"
import PortfolioGraph from "../../components/portfolioGraph/PortfolioGraph"
import Header from "../../components/header/Header"
import styles from "./Portfolio.module.css"

export default function Portfolio() {

    return (
        <div>
            <Header />
            <PortfolioGraph />
            <PortfolioTable />
        </div>
    )
}

