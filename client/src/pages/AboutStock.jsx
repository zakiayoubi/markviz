import { useState, useEffect } from "react"
import {api} from "../services/api"
import { useParams } from "react-router-dom"

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
        <div>
            <h2>About</h2>
            <p>{about.summary}</p>
            <p>{about.ceo}</p>
            <p>{about.founded}</p>
            <p>{about.headquarters}</p>
            <p>{about.employees}</p>
            <a href={about.website}>{about.website}</a>
        </div>
    )
}

