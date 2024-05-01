import { Link } from "react-router-dom";
import '../Home.css';

const TenantView = () => {

    return (
        <div className="home-page">
            <h2>Welcome to Tenant page</h2>
            <div className="home-page__links">
                {<Link to="/create_request" className="home-page__link">Create Request</Link>}
                {<Link to="/view_request" className="home-page__link">View Request</Link>}
                {<Link to="/view_requests" className="home-page__link">View My Requests</Link>}
                {<Link to="/update_request" className="home-page__link">Update Request</Link>}
            </div>
            <div className="home-page__button">
                <Link to="/home">Back</Link>
            </div>
        </div>
    );
}

export default TenantView