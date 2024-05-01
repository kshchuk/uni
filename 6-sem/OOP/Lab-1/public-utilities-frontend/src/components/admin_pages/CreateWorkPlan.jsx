import { Link } from "react-router-dom"
import "../pages/Entity.css"
import "../Home.css"
import axios from "../../api/axios"
import { useState } from "react"
import getHeaderConfig from "../hooks/Config"

const SET_URL = "/workplan"

const CreateWorkPlan = () => {

    const [data, setData] = useState([]);
    const [id, setID] = useState('');

    const [description, setDescription] = useState('');
    const [duration, setDuration] = useState('');
    const [teamId, setTeamId] = useState('');

    const config = getHeaderConfig();

    const makeRequest = async (field, value) => {
        console.log(config);
        const response = await axios.get(SET_URL, {
            params: {
                field: field,
                value: value
            },
            headers : config.headers
        });
        console.log(JSON.stringify(response?.data));
        setData(response?.data);
    }

    const makeCreate = async () => {
        const response = await axios.post(SET_URL, JSON.stringify({
            workPlanId: "",
            description: description,
            duration: duration,
            teamId: teamId
        }), config);
        setData(response?.data);
        setDescription("");
        setDuration("");
        setTeamId("");
    }

    return (
        <section>
            <h2>Work Plans</h2>
            <div className="queries">
                <div>
                    <label htmlFor="byID">Query by ID</label>
                    <input type="text" id="byID" onChange={(e) => setID(e.target.value)} value={id} />
                    <button onClick={() => makeRequest("id", id)}>Execute Query</button>
                </div>
                <div>
                    <label htmlFor="all">Query All</label>
                    <button id="all" onClick={() => makeRequest("all", "all")}>Execute Query</button>
                </div>
            </div>
            <p>You can create new work plans</p>
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
                    <tr>
                        <td>Create new:</td>
                        <td><input type="text" onChange={(e) => setDescription(e.target.value)} value={description}></input></td>
                        <td><input type="text" onChange={(e) => setDuration(e.target.value)} value={duration}></input></td>
                        <td><input type="text" onChange={(e) => setTeamId(e.target.value)} value={teamId}></input></td>
                        <td><button onClick={() => makeCreate()}>Create</button></td>
                    </tr>
                    {data?.map((item) => (
                        <tr key={item.workPlanId}>
                            <td>{item.workPlanId}</td>
                            <td>{item.description}</td>
                            <td>{item.duration}</td>
                            <td>{item.teamId}</td>
                        </tr>
                    ))}
                    </tbody>
                </table>
            </div>
            <div className="home-page__button">
                <Link to="/view">Back</Link>
            </div>
        </section>
    )
}

export default CreateWorkPlan
