import { Link } from "react-router-dom";
import '../Home.css';

const TenantView = () => {

    return (
        <div className="home-page">
            <h2>Welcome to Tenant page</h2>
            <div className="home-page__links">
                {<Link to="/edit_requests"  className="home-page__link">Edit Requests</Link>}
            </div>
            <div className="home-page__button">
                <Link to="/home">Back</Link>
            </div>
        </div>
    );
}

export default TenantView