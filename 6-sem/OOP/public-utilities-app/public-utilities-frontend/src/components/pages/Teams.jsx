import { Link } from "react-router-dom"
import "./Entity.css"
import "../Home.css"
import axios from "../../api/axios"
import {useEffect, useState} from "react"
import getHeaderConfig from "../hooks/Config"
const TEAM_URL = "/team";
const SPECIALIST_URL = "/specialist";

const Teams = () => {
    const [data, setData] = useState([]);
    const [id, setID] = useState('');
    const [specialists, setSpecialists] = useState([]);
    const [workplans, setWorkplans] = useState([]);
    const [dispatcher, setDispatcher] = useState({});

    const config = getHeaderConfig();

    const makeRequest = async (field, value) => {
        console.log("Making request");
        let url;
        if (field === 'all' && value === 'all') {
            url = `${TEAM_URL}/all`;
        } else {
            url = `${TEAM_URL}/?${field}=${value}`;
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

    const getSpecialists = async (teamId) => {
        console.log("Getting specialists");
        let url = `${TEAM_URL}/specialists?id=${teamId}`;

        try {
            const response = await axios.get(url, {
                headers: config.headers
            });
            console.log(JSON.stringify(response.data));

            setSpecialists(response.data);
        } catch (error) {
            console.error("Error getting specialists:", error.message);
        }
    }

    const getWorkPlans = async (teamId) => {
        console.log("Getting work plans");
        let url = `${TEAM_URL}/workplans?id=${teamId}`;

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

    const getDispatcher = async (dispatcherId) => {
        console.log("Getting dispatcher");
        let url = `${SPECIALIST_URL}/?id=${dispatcherId}`;

        try {
            const response = await axios.get(url, {
                headers: config.headers
            });
            console.log(JSON.stringify(response.data));
            setDispatcher(response.data);
        } catch (error) {
            console.error("Error getting dispatcher:", error.message);
        }
    }

    useEffect(() => {
        makeRequest("all", "all");
    }, []);

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
                        <tr key={item.teamId}>
                            <td>{item.teamId}</td>
                            <td>{item.dispatcherId}</td>
                            <td>{item.specialistIds ? item.specialistIds.length : 0}</td>
                            <td>{item.workPlanIds ? item.workPlanIds.length : 0}</td>
                            <td>
                                <button onClick={() => getSpecialists(item.teamId)}>Get Specialists</button>
                            </td>
                            <td>
                                <button onClick={() => getWorkPlans(item.teamId)}>Get Work Plans</button>
                            </td>
                            <td>
                                <button onClick={() => getDispatcher(item.dispatcherId)}>Get Dispatcher</button>
                            </td>
                        </tr>
                    ))}
                    </tbody>
                </table>
            </div>
            <div className="queries">
                <div>
                    <label htmlFor="byID">Query by ID</label>
                    <input type="text" id="byID" onChange={(e) => setID(e.target.value)} value={id}/>
                    <button onClick={() => makeRequest("id", id)}>Execute Query</button>
                </div>
                <div>
                    <label htmlFor="all">Query All</label>
                    <button id="all" onClick={() => makeRequest("all", "all")}>Execute Query</button>
                </div>
            </div>
            <div className="home-page__button">
                <Link to="/view">Back</Link>
            </div>

            <div className={"container"}>
                <h2>Team Specialists</h2>
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
                    {specialists?.map((item, index) => (
                        <tr key={index}>
                            <td>{item.specialistId}</td>
                            <td>{item.name}</td>
                            <td>{item.specialization}</td>
                            <td>{item.teamId ? item.teamId : "None"}</td>
                            <td>{item.workPlanIds ? item.workPlanIds.length : 0}</td>
                        </tr>
                    ))}
                    </tbody>
                </table>
            </div>
            <div className="container">
                <h2>Team WorkPlans</h2>
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
                    {
                        workplans?.map((item, index) => (
                        <tr key={index}>
                            <td>{item.workPlanId}</td>
                            <td>{item.description}</td>
                            <td>{item.duration}</td>
                            <td>{item.teamId}</td>
                        </tr>
                        ))
                    }
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
                        <th>Team ID</th>
                        <th>Work Plan IDs</th>
                    </tr>
                    </thead>
                    <tbody>
                        <tr key={dispatcher.specialistId}>
                            <td>{dispatcher.specialistId}</td>
                            <td>{dispatcher.name}</td>
                            <td>{dispatcher.specialization}</td>
                            <td>{dispatcher.teamId ? dispatcher.teamId : "None"}</td>
                            <td>{dispatcher.workPlanIds ? dispatcher.workPlanIds.length : 0}</td>
                        </tr>
                    </tbody>
                </table>
            </div>
        </section>
    )
}

export default Teams
