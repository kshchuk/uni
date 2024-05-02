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
    const [id, setID] = useState('');

    const config = getHeaderConfig();

    const makeRequest = async (field, value) => {
        console.log("Making request");
        let url;
        if (field === 'all' && value === 'all') {
            url = `${SPECIALIST_URL}/all`;
        } else {
            url = `${SPECIALIST_URL}/?${field}=${value}`;
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

    const getWorkPlanIds = async (specialistId) => {
        const response = await axios.get(`${SPECIALIST_URL}/workplans`, {
            params: {
                id: specialistId
            },
            headers: config.headers
        });
        console.log(JSON.stringify(response?.data));
        setData(response?.data);

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
                        <tr key={item.id}>
                            <td>{item.id}</td>
                            <td>{item.name}</td>
                            <td>{item.specialization}</td>
                            <td>{item.teamId}</td>
                            <td>{item.workPlanIds.join(", ")}</td>
                            <td>
                                <button onClick={() => getWorkPlanIds(item.specialistId)}>Get Work Plan IDs</button>
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
                    {workplans?.map((workplan, index) => (
                        <li key={index}>{workplan.id}: {workplan.description}, {workplan.duration}, {workplan.teamId}</li>
                    ))}
                </ul>
            </div>
        </section>
    )
}

export default Specialists
