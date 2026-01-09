import { useEffect, useState } from "react";
import { useParams } from "react-router-dom"
import {api} from "../../services/api"
import PriceChart from "../../components/priceChart/PriceChart"
import AboutStock from "../../components/aboutStock/AboutStock";
import StockStats from "../../components/stockStats/StockStats";
import Header from "../../components/header/Header";
import styles from "./Stock.module.css"

export default function Stock() {
    return (
        <div>
            <Header></Header>
            <div className={styles.container}>
                <div className={styles.graphAboutContainer}>
                    <PriceChart />
                    <AboutStock />
                </div>
                <StockStats></StockStats>
            </div>
            
        </div>
    )
}

