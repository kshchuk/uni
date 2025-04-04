import { Link } from "react-router-dom";
import "./Entity.css";
import "../Home.css";
import axios from "../../api/axios";
import { useState, useEffect } from "react";
import getHeaderConfig from "../hooks/Config";

const WORKPLAN_URL = "/work-plan";

const WorkPlans = () => {
    const [data, setData] = useState([]);
    const [id, setID] = useState('');
    const config = getHeaderConfig();

    const makeRequest = async (endpoint) => {
        console.log("Making request");
        console.log(config.headers);
        const url = `${WORKPLAN_URL}/${endpoint}`;

        try {
            const response = await axios.get(url, { headers: config.headers });
            console.log(JSON.stringify(response.data));
            setData(response.data);
        } catch (error) {
            console.error("Error making request:", error.message);
        }
    };

    useEffect(() => {
        makeRequest("all");
    }, []);

    const formatDuration = (duration) => {
        const { hours, minutes } = duration;
        return `${hours}h ${minutes}m`;
    };

    return (
        <section>
            <h2>Work Plans</h2>
            <p>You can query data about work plans</p>
            <div className="container">
                <h2>Data Table</h2>
                <table>
                    <thead>
                    <tr>
                        <th>Work Plan ID</th>
                        <th>Description</th>
                        <th>Duration</th>
                        <th>Team ID</th>
                    </tr>
                    </thead>
                    <tbody>
                    {data?.map((item) => (
                        <tr key={item.id}>
                            <td>{item.id}</td>
                            <td>{item.description}</td>
                            <td>{formatDuration(item.duration)}</td>
                            <td>{item.team.id}</td>
                        </tr>
                    ))}
                    </tbody>
                </table>
            </div>
            <div className="queries">
                <div>
                    <label htmlFor="byID">Query by ID</label>
                    <input type="text" id="byID" onChange={(e) => setID(e.target.value)} value={id} />
                    <button onClick={() => makeRequest(id)}>Execute Query</button>
                </div>
                <div>
                    <label htmlFor="all">Query All</label>
                    <button onClick={() => makeRequest("all")}>All</button>
                </div>
            </div>
            <div className="home-page__button">
                <Link to="/">Back</Link>
            </div>
        </section>
    );
};

export default WorkPlans;
