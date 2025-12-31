import styles from "./Footer.module.css"

function Footer() {
    const year = new Date().getFullYear();
    return (
        <footer className={styles.footer}>
            <p>Copyright ⓒ {year} MarkViz</p>
        </footer>
    );
}

export default Footer;