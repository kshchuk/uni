import { Link } from "react-router-dom";
import "./Entity.css";
import "../Home.css";
import axios from "../../api/axios";
import { useState, useEffect } from "react";
import getHeaderConfig from "../hooks/Config";

const SPECIALIST_URL = "/specialist";
const WORKPLAN_URL = "/work-plan";

const Specialists = () => {
    const [data, setData] = useState([]);
    const [workplans, setWorkplans] = useState([]);
    const [id, setID] = useState('');

    const config = getHeaderConfig();

    const makeRequest = async (endpoint) => {
        console.log("Making request");
        console.log(config.headers);
        const url = `${SPECIALIST_URL}/${endpoint}`;

        try {
            const response = await axios.get(url, { headers: config.headers });
            console.log(JSON.stringify(response.data));
            setData(response.data);
        } catch (error) {
            console.error("Error making request:", error.message);
        }
    };

    const getWorkPlans = async (dispatcherId) => {
        console.log("Getting work plans");
        const url = `${WORKPLAN_URL}/dispatcher/${dispatcherId}`;

        try {
            const response = await axios.get(url, { headers: config.headers });
            console.log(JSON.stringify(response.data));
            setWorkplans(response.data);
        } catch (error) {
            console.error("Error getting work plans:", error.message);
        }
    };

    useEffect(() => {
        makeRequest("all");
    }, []);

    const formatDuration = (duration) => {
        if (!duration) return '';
        const { hours = 0, minutes = 0 } = duration;
        return `${hours}h ${minutes}m`;
    };

    return (
        <section>
            <h2>Specialists</h2>
            <p>You can query data about specialists</p>
            <div className="container">
                <h2>Data Table</h2>
                <table>
                    <thead>
                    <tr>
                        <th>Specialist ID</th>
                        <th>Name</th>
                        <th>Specialization</th>
                        <th>Team ID</th>
                        <th colSpan={1}>Actions</th>
                    </tr>
                    </thead>
                    <tbody>
                    {data?.map((item) => (
                        <tr key={item.id}>
                            <td>{item.id}</td>
                            <td>{item.name}</td>
                            <td>{item.specialization}</td>
                            <td>{item.team != undefined ? item.team.id : "Dispatcher"}</td>
                            <td>
                                <button onClick={() => getWorkPlans(item.id)}>Get Work Plan IDs</button>
                            </td>
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
            </div>
            <div className="home-page__button">
                <Link to="/">Back</Link>
            </div>
            <div className="container">
                <h2>Specialist Work Plans</h2>
                <p>Get work plans for a dispatcher</p>
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
                    {workplans?.map((workplan, index) => (
                        <tr key={index}>
                            <td>{workplan.id}</td>
                            <td>{workplan.description}</td>
                            <td>{formatDuration(workplan.duration)}</td>
                            <td>{workplan.team?.id || "N/A"}</td>
                        </tr>
                    ))}
                    </tbody>
                </table>
            </div>
        </section>
    );
};

export default Specialists;
