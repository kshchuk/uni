import { Link } from "react-router-dom";
import '../Home.css';

const AdminView = () =>{

    return (
        <div className="home-page">
            <h2>Welcome to Admin page</h2>
            <div className="home-page__links">
                {<Link to="/view_requests" className="home-page__link">View Requests</Link>}
                {<Link to="/view_specialists" className="home-page__link">View Specialists</Link>}
                {<Link to="/view_teams" className="home-page__link">View Teams</Link>}
                {<Link to="/view_work_plans" className="home-page__link">View Work Plans</Link>}
                {<Link to="/view_tenants" className="home-page__link">View Tenants</Link>}
            </div>
            <div className="home-page__button">
                <Link to="/home">Back</Link>
            </div>
        </div>
    );
}

export default AdminView