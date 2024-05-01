import { Link } from "react-router-dom";
import '../Home.css';

/*
Housing and communal services system. The tenant sends an Application, in which he indicates the type
(electrical, plumbing...) and scope of work and the desired time of execution. The Dispatcher forms a
Team of relevant Specialists and registers it in the Work Plan.
 */

const DispatcherView = () =>{

    return (
        <div className="home-page">
            <h2>Welcome to Dispatcher page</h2>
            <div className="home-page__links">
                {<Link to="/create_team" className="home-page__link">Create Team</Link>}
                {<Link to="/view_team" className="home-page__link">View Team</Link>}
                {<Link to="/create_work_plan" className="home-page__link">Create Work Plan</Link>}
                {<Link to="/view_work_plan" className="home-page__link">View Work Plan</Link>}
                {<Link to="/view_requests" className="home-page__link">View Requests</Link>}
                {<Link to="/view_specialists" className="home-page__link">View Specialists</Link>}
                {<Link to="/view_teams" className="home-page__link">View Teams</Link>}
                {<Link to="/view_work_plans" className="home-page__link">View Work Plans</Link>}
                {<Link to="/update_request" className="home-page__link">Update Request</Link>}
            </div>
            <div className="home-page__button">
                <Link to="/home">Back</Link>
            </div>
        </div>
    );
}

export default DispatcherView