import { Link } from "react-router-dom"
import "./Entity.css"
import "../Home.css"
import axios from "../../api/axios"
import {useEffect, useState} from "react"
import getHeaderConfig from "../hooks/Config"
const WORKPLAN_URL = "/work-plan";
const TEAM_URL = "/team"

const WorkPlans = () => {
    const [data, setData] = useState([]);
    const [id, setID] = useState('');
    const [team, setTeam] = useState({})

    const config = getHeaderConfig();

    const makeRequest = async (field, value) => {
        console.log("Making request");
        let url;
        if (field === 'all' && value === 'all') {
            url = `${WORKPLAN_URL}/all`;
        } else {
            url = `${WORKPLAN_URL}/?${field}=${value}`;
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

    const getTeam = async (teamId) => {
        console.log("Making request:")
        let url = `${TEAM_URL}/?id=${teamId}`

        try {
            const response = await axios.get(url, {
                headers: config.headers
            });
            console.log(JSON.stringify(response.data))
            setTeam(response.data)
        } catch (error) {
            console.error("Error making request:", error.message);
        }
    }

    useEffect(() => {
        makeRequest("all", "all");
    }, []);

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
                        <th>Actions</th>
                    </tr>
                    </thead>
                    <tbody>
                    {data?.map((item) => (
                        <tr key={item.workPlanId}>
                            <td>{item.workPlanId}</td>
                            <td>{item.description}</td>
                            <td>{item.duration}</td>
                            <td>{item.teamId}</td>
                            <td>
                                <button onClick={() => getTeam(item.teamId)}> Get Team</button>
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

            <div className="container">
                <h2>WorkPlan Team</h2>
                <table>
                    <thead>
                    <tr>
                        <th>Team ID</th>
                        <th>Dispatcher ID</th>
                        <th>Specialist IDs</th>
                        <th>Work Plan IDs</th>
                    </tr>
                    </thead>
                    <tbody>
                        <tr key={team.teamId}>
                            <td>{team.teamId}</td>
                            <td>{team.dispatcherId}</td>
                            <td>{team.specialistIds ? team.specialistIds.length : 0}</td>
                            <td>{team.workPlanIds ? team.workPlanIds.length : 0}</td>
                        </tr>
                    </tbody>
                </table>
            </div>

        </section>
    )
}

export default WorkPlans
