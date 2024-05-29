import { Link } from "react-router-dom";
import "./Entity.css";
import "../Home.css";
import axios from "../../api/axios";
import { useState, useEffect } from "react";
import getHeaderConfig from "../hooks/Config";

const TEAM_URL = "/team";
const SPECIALIST_URL = "/specialist";
const WORKPLAN_URL = "/work-plan";

const Teams = () => {
    const [data, setData] = useState([]);
    const [id, setID] = useState('');
    const [specialists, setSpecialists] = useState([]);
    const [workplans, setWorkplans] = useState([]);
    const [dispatcher, setDispatcher] = useState({});
    const [specialistCounts, setSpecialistCounts] = useState({});
    const [workPlanCounts, setWorkPlanCounts] = useState({});

    const config = getHeaderConfig();

    const makeRequest = async (endpoint) => {
        console.log("Making request");
        console.log(config.headers);
        const url = `${TEAM_URL}/${endpoint}`;

        try {
            const response = await axios.get(url, { headers: config.headers });
            console.log(JSON.stringify(response.data));
            setData(response.data);
        } catch (error) {
            console.error("Error making request:", error.message);
        }
    };

    const getSpecialists = async (teamId) => {
        console.log("Getting specialists");
        const url = `${SPECIALIST_URL}/team/${teamId}`;

        try {
            const response = await axios.get(url, { headers: config.headers });
            console.log(JSON.stringify(response.data));
            setSpecialists(response.data);
        } catch (error) {
            console.error("Error getting specialists:", error.message);
        }
    };

    const getWorkPlans = async (teamId) => {
        console.log("Getting work plans");
        const url = `${WORKPLAN_URL}/team/${teamId}`;

        try {
            const response = await axios.get(url, { headers: config.headers });
            console.log(JSON.stringify(response.data));
            setWorkplans(response.data);
        } catch (error) {
            console.error("Error getting work plans:", error.message);
        }
    };

    const getDispatcher = async (dispatcherId) => {
        console.log("Getting dispatcher");
        const url = `${SPECIALIST_URL}/${dispatcherId}`;

        try {
            const response = await axios.get(url, { headers: config.headers });
            console.log(JSON.stringify(response.data));
            setDispatcher(response.data);
        } catch (error) {
            console.error("Error getting dispatcher:", error.message);
        }
    };

    const getSpecialistCount = async (teamId) => {
        const url = `${SPECIALIST_URL}/team/${teamId}/count`;

        try {
            const response = await axios.get(url, { headers: config.headers });
            console.log(JSON.stringify(response.data));
            setSpecialistCounts(prevCounts => ({ ...prevCounts, [teamId]: response.data }));
        } catch (error) {
            console.error("Error getting specialist count:", error.message);
        }
    };

    const getWorkPlanCount = async (teamId) => {
        const url = `${WORKPLAN_URL}/team/${teamId}/count`;

        try {
            const response = await axios.get(url, { headers: config.headers });
            console.log(JSON.stringify(response.data));
            setWorkPlanCounts(prevCounts => ({ ...prevCounts, [teamId]: response.data }));
        } catch (error) {
            console.error("Error getting work plan count:", error.message);
        }
    };

    const formatDuration = (duration) => {
        if (!duration) return '';
        const { hours = 0, minutes = 0 } = duration;
        return `${hours}h ${minutes}m`;

    }

    useEffect(() => {
        makeRequest("all");
    }, []);

    useEffect(() => {
        data.forEach(item => {
            getSpecialistCount(item.id);
            getWorkPlanCount(item.id);
        });
    }, [data]);

    return (
        <section>
            <h2>Teams</h2>
            <p>You can query data about teams</p>
            <div className="container">
                <h2>Data Table</h2>
                <table>
                    <thead>
                    <tr>
                        <th>Team ID</th>
                        <th>Dispatcher ID</th>
                        <th>Specialist IDs</th>
                        <th>Work Plan IDs</th>
                        <th colSpan={3}>Actions</th>
                    </tr>
                    </thead>
                    <tbody>
                    {data?.map((item) => (
                        <tr key={item.id}>
                            <td>{item.id}</td>
                            <td>{item.dispatcher.id}</td>
                            <td>{specialistCounts[item.id] || 0}</td>
                            <td>{workPlanCounts[item.id] || 0}</td>
                            <td>
                                <button onClick={() => getSpecialists(item.id)}>Get Specialists</button>
                            </td>
                            <td>
                                <button onClick={() => getWorkPlans(item.id)}>Get Work Plans</button>
                            </td>
                            <td>
                                <button onClick={() => getDispatcher(item.dispatcher.id)}>Get Dispatcher</button>
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
                <div>
                    <label htmlFor="all">Query All</label>
                    <button id="all" onClick={() => makeRequest("all")}>Execute Query</button>
                </div>
            </div>
            <div className="home-page__button">
                <Link to="/">Back</Link>
            </div>
            <div className="container">
                <h2>Team Specialists</h2>
                <table>
                    <thead>
                    <tr>
                        <th>Specialist ID</th>
                        <th>Name</th>
                        <th>Specialization</th>
                        <th>Team ID</th>
                    </tr>
                    </thead>
                    <tbody>
                    {specialists?.map((item, index) => (
                        <tr key={index}>
                            <td>{item.id}</td>
                            <td>{item.name}</td>
                            <td>{item.specialization}</td>
                            <td>{item.team?.id || "None"}</td>
                        </tr>
                    ))}
                    </tbody>
                </table>
            </div>
            <div className="container">
                <h2>Team Work Plans</h2>
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
                    {workplans?.map((item, index) => (
                        <tr key={index}>
                            <td>{item.id}</td>
                            <td>{item.description}</td>
                            <td>{formatDuration(item.duration)}</td>
                            <td>{item.team.id}</td>
                        </tr>
                    ))}
                    </tbody>
                </table>
            </div>
            <div className="container">
                <h2>Team Dispatcher</h2>
                <table>
                    <thead>
                    <tr>
                        <th>Specialist ID</th>
                        <th>Name</th>
                        <th>Specialization</th>
                    </tr>
                    </thead>
                    <tbody>
                    <tr>
                        <td>{dispatcher.id}</td>
                        <td>{dispatcher.name}</td>
                        <td>{dispatcher.specialization}</td>
                    </tr>
                    </tbody>
                </table>
            </div>
        </section>
    );
};

export default Teams;
