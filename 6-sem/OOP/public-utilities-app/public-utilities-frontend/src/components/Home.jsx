import { useNavigate, Link } from "react-router-dom";
import { useContext } from "react";
import AuthContext from "./context/AuthProvider";
import './Home.css'; 

const Home = () => {
    const { setAuth } = useContext(AuthContext);
    const navigate = useNavigate();

    return (
        <section className="home-page">
            <h1>Home</h1>
            <p className="home-page__description">You are logged in!</p>
            <div className="home-page__links">
                <Link to="admin/view" className="home-page__link">Admin View</Link>
            </div>
            <div className="home-page__links">
                <Link to="tenant/view" className="home-page__link">Tenant View</Link>
            </div>
            <div className="home-page__links">
                <Link to="dispatcher/view" className="home-page__link">Dispatcher View</Link>
            </div>
            {/*<div className="home-page__button">*/}
            {/*    <button onClick={logout} className="home-page__button-text">Sign Out</button>*/}
            {/*</div>*/}
        </section>
    )
}

export default Home