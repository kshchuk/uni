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
                <Link to={"/view_drequests"} className="home-page__link">View Requests</Link>
                {<Link to="/edit_teams" className="home-page__link">Manage Teams</Link>}
                {<Link to="/edit_workplans" className="home-page__link">Manage WorkPlans</Link>}
            </div>
            <div className="home-page__button">
                <Link to="/home">Back</Link>
            </div>
        </div>
    );
}

export default DispatcherView