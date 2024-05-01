import { Link } from "react-router-dom";
import '../Home.css';

const View = () =>{

    return (
        <div className="home-page">
            <h2>Welcome to Viewing page</h2>
            <div className="home-page__links">
                {/*<Link to="/crew_view" className="home-page__link">Query Crew data</Link>*/}
                {/*<Link to="/brigade_view" className="home-page__link">Query Brigade data</Link>*/}
                {/*<Link to="/planes_view" className="home-page__link">Query Planes data</Link>*/}
                {/*<Link to="/races_view" className="home-page__link">Query Races data</Link>*/}
                {/* <Link to="/flights_view" className="home-page__link">Query WorkPlan data</Link> */}
            </div>
            <div className="home-page__button">
                <Link to="/home">Back</Link>
            </div>
        </div>
    );
}

export default View