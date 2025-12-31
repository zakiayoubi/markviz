export default function PrimaryButton({ children, onClick, type = "button" }) {
    return (
        <button className="btn-primary" onClick={onClick} type={type}>
            {children}
        </button>
    );
}