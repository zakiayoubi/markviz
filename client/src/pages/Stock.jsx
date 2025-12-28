import { useEffect, useState } from "react";
import { useParams } from "react-router-dom"
import {api} from "../services/api"
import PriceChart from "./PriceChart";
import AboutStock from "./AboutStock";
import StockStats from "./StockStats";
import Header from "./Header";

export default function Stock() {
    return (
        <div>
            Stock Detail Page
            <Header></Header>
            <PriceChart></PriceChart>
            <AboutStock></AboutStock>
            <StockStats></StockStats>
        </div>
    )
}

