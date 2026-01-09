import Treemap from "../../components/treemap/Treemap";
import Header from "../../components/header/Header";
import styles from "./Home.module.css";

export default function Home() {

    return (
        <div>
            <Header />
            <h1 className={styles.title}>S&P 500 Index</h1>
            <Treemap />
        </div>
    )
}