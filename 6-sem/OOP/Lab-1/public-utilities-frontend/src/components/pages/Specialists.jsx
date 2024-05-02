import { Link } from "react-router-dom"
import "./Entity.css"
import "../Home.css"
import axios from "../../api/axios"
import { useState, useEffect } from "react"
import getHeaderConfig from "../hooks/Config"
const SPECIALIST_URL = "/specialist";

const Specialists = () => {
    const [data, setData] = useState([]);
    const [workplans, setWorkplans] = useState([]);
    const [team, setTeam] = useState([]);
    const [id, setID] = useState('');

    const config = getHeaderConfig();

    const makeRequest = async (field, value) => {
        console.log("Making request");
        let url;
        if (field === 'all' && value === 'all') {
            url = `${SPECIALIST_URL}/all`;
        } else {
            url = `${SPECIALIST_URL}?${field}=${value}`;
        }

        try {
            const response = await axios.get(url, {
                headers: config.headers
            });
            console.log(JSON.stringify(response.data));
            setData(response.data);
        } catch (error) {
            console.error("Error making request:", error.message);
        }
    }

    const getWorkPlans = async (specialistId) => {
        console.log("Getting work plans");
        let url = `${SPECIALIST_URL}/workplans/?id=${specialistId}`;

        try {
            const response = await axios.get(url, {
                headers: config.headers
            });
            console.log(JSON.stringify(response.data));
            setWorkplans(response.data);
        } catch (error) {
            console.error("Error getting work plans:", error.message);
        }
    }

    const getTeam = async (teamId) => {
        if (teamId === null) {
            return;
        }
        console.log("Getting team");
        let url = `$/team/?id=${teamId}`;

        try {
            const response = await axios.get(url, {
                headers: config.headers
            });
            console.log(JSON.stringify(response.data));
            setTeam(response.data);
        } catch (error) {
            console.error("Error getting team:", error.message);
        }

    }

    useEffect(() => {
        makeRequest("all", "all");
    }, []);

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
                        <th>Work Plan IDs</th>
                    </tr>
                    </thead>
                    <tbody>
                    {data?.map((item) => (
                        <tr key={item.specialistId}>
                            <td>{item.specialistId}</td>
                            <td>{item.name}</td>
                            <td>{item.specialization}</td>
                            <td>{item.teamId ? item.teamId : "None"}</td>
                            <td>{item.workPlanIds ? item.workPlanIds.length : 0}</td>
                            <td>
                                <button onClick={() => getWorkPlans(item.specialistId)}>Get Work Plan IDs</button>
                            </td>
                            <td>
                                <button onClick={() => getTeam(item.teamId)}>Get Team</button>
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
                    <button onClick={() => makeRequest("id", id)}>Execute Query</button>
                </div>
            </div>
            <div className="home-page__button">
                <Link to="/view">Back</Link>
            </div>
            <div>
                <h2>Specialist Work Plans</h2>
                <p>Get work plans for a specialist</p>
                <ul>
                    <div>
                        {workplans?.map((workplan, index) => (
                            <div key={index}>
                                <h3>Work Plan ID: {workplan.workPlanId}</h3>
                                <p>Description: {workplan.description}</p>
                                <p>Duration: {workplan.duration}</p>
                                <p>Team ID: {workplan.teamId}</p>
                            </div>
                        ))}
                    </div>
                    <div>
                        <h2>Team</h2>
                        <ul>
                            {team?.map((item, index) => (
                                <li key={index}>
                                    <p>Team ID: {item.teamId}</p>
                                    <p>Dispatcher ID: {item.dispatcherId}</p>
                                    <p>Specialist IDs: {item.specialistIds.join(", ")}</p>
                                    <p>Work Plan IDs: {item.workPlanIds.join(", ")}</p>
                                </li>
                            ))}
                        </ul>
                    </div>
                </ul>
            </div>
        </section>
    )
}

export default Specialists
