import { useState, useEffect } from "react"
import {api} from "../../services/api"
import { useParams } from "react-router-dom"
import styles from "./AboutStock.module.css"

export default function AboutStock() {
    const [about, setAbout] = useState()
    const [loading, setLoading] = useState(true)
    const { ticker } = useParams()

    useEffect(() => {
        const fetchAbout = async () => {
            try {
                const response = await api.get(`/stocks/about/${ticker}`)
                setAbout(response.data)
            } catch (err) {
                console.log(err)
            } finally {
                setLoading(false)
            }
        }
        fetchAbout()
    }, [ticker])

    if (loading) return (<div> Loading ...</div>)
    if (!about) return (<div> Data not Available</div>)
    return (
        <div className={styles.container}>
            <h2>About</h2>
            <p>{about.summary}</p>
            <div className={styles.detail}>
                <h3>CEO</h3>
                <p>{about.ceo}</p>
            </div>
            <div className={styles.detail}>
                <h3>Headquarters</h3>
                <p>{about.headquarters}</p>
            </div>
            <div className={styles.detail}>
                <h3>Employees</h3>
                <p>{about.employees}</p>
            </div>
            <div className={styles.detail}>
                <h3>Website</h3>
                <a href={about.website}>{about.website}</a>
            </div>
        </div>
    )
}

