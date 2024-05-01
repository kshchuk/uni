import { useNavigate } from "react-router-dom"
import "./Unauthorized.css"

const Unauthorized = () => {
    const navigate = useNavigate();

    const goBack = () => navigate(-1);

    return (
        <section className="unauthorized-page">
            <h1>Unauthorized</h1>
            <p className="unauthorized-page__description">You do not have access to the requested page.</p>
            <div className="unauthorized-page__button">
                <button className="unauthorized-page__button-text" onClick={goBack}>Go Back</button>
            </div>
        </section>
    )
}

export default Unauthorized