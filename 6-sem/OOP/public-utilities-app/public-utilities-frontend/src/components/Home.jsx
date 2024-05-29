import { Link } from "react-router-dom";
import './Home.css';
import {useContext} from "react";
import AuthContext from "./context/AuthProvider";
import { Navigate } from "react-router-dom";

const Home = () => {
    let auth = useContext(AuthContext);

    return (
        <section className="home-page">
            <h1>Home</h1>
            <p className="home-page__description">You are logged in!</p>
            <div className="home-page__links">
                <Link to="/admin_view" className="home-page__link">Admin View</Link>
            </div>
            <div className="home-page__links">
                <Link to="/tenant_view" className="home-page__link">Tenant View</Link>
            </div>
            <div className="home-page__links">
                <Link to="/dispatcher_view" className="home-page__link">Dispatcher View</Link>
            </div>
            <div className="home-page__button">
                <button onClick={auth.logout} className="home-page__button-text">Sign Out</button>
            </div>
        </section>
    )
}

export default Home