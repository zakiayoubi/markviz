import styles from "./Layout.module.css"
import Footer from "../../components/footer/Footer"
export default function Layout({ children }) {
    return (
        <div className={styles.layout}>
            {children}
            <Footer />
        </div>
    );
}