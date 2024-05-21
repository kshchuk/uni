import { Link } from "react-router-dom"
import "../pages/Entity.css"
import "../Home.css"
import axios from "../../api/axios"
import {useEffect, useState} from "react"
import getHeaderConfig from "../hooks/Config"

const WORKPLAN_URL = "/work-plan"
const TEAM_URL = "/team"

const EditWorkPlans = () => {
    const [data, setData] = useState([]);
    const [teams, setTeams] = useState([]);

    const [description, setDescription] = useState('');
    const [duration, setDuration] = useState('');
    const [selectedTeamId, setSelectedTeamId] = useState('');

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

    const fetchTeams = async () => {
        let url = `${TEAM_URL}/all`;

        try {
            const response = await axios.get(url, {
                headers: config.headers
            });
            console.log(JSON.stringify(response.data));
            if (Array.isArray(response.data)) {
                setTeams(response.data);
            } else {
                setTeams([response.data]);
            }
        } catch (error) {
            console.error("Error fetching teams:", error.message);
        }
    };

    const makeEdit = async (id) => {
        const editItem = data.find((item) => item.workPlanId === id);
        const response = await axios.put(WORKPLAN_URL, JSON.stringify({
            workPlanId: editItem.workPlanId,
            description: editItem.description,
            duration: editItem.duration,
            teamId: editItem.teamId
        }), config);
    };

    const makeDelete = async (id) => {
        let url = `${WORKPLAN_URL}/?id=${id}`;
        const response = await axios.delete(url, config);
        if (response.status !== 200) {
            console.error("Error deleting item");
            return;
        }
        setData((prevData) => prevData.filter(item => item.workPlanId !== id));
    };

    const makeCreate = async () => {
        await axios.post(WORKPLAN_URL, JSON.stringify({
            description: description,
            duration: duration,
            teamId: selectedTeamId
        }), config);
        setDescription("");
        setDuration("");
        setSelectedTeamId("");
        makeRequest("all", "all");
    };

    useEffect(() => {
        makeRequest("all", "all"); // Fetch data when page loads
        fetchTeams(); // Fetch teams when page loads
    }, []);

    return (
        <section>
            <h2>Work Plans</h2>
            <div className="queries">
                <div>
                    <label htmlFor="byID">Query by Work Plan ID</label>
                    <input type="text" id="byID" onChange={(e) => makeRequest("id", e.target.value.trimEnd())} />
                </div>
            </div>
            <p>You can edit data about work plans</p>
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
                        <td><select onChange={(e) => setSelectedTeamId(e.target.value)}>
                            {teams.map((team) => (
                                <option value={team.teamId}>{team.teamId}</option>
                            ))}
                        </select></td>
                        <td><button onClick={() => makeCreate()}>Create</button></td>
                    </tr>
                    {data?.map((item) => (
                        <tr key={item.workPlanId}>
                            <td>{item.workPlanId}</td>
                            <td><input
                                type="text"
                                value={item.description}
                                onChange={(e) => {
                                    const newData = [...data];
                                    newData.find((el) => el.workPlanId === item.workPlanId).description = e.target.value;
                                    setData(newData);
                                }}
                            /></td>
                            <td><input
                                type="text"
                                value={item.duration}
                                onChange={(e) => {
                                    const newData = [...data];
                                    newData.find((el) => el.workPlanId === item.workPlanId).duration = e.target.value;
                                    setData(newData);
                                }}
                            /></td>
                            <td><input
                                type="text"
                                value={item.teamId}
                                onChange={(e) => {
                                    const newData = [...data];
                                    newData.find((el) => el.workPlanId === item.workPlanId).teamId = e.target.value;
                                    setData(newData);
                                }}
                            /></td>
                            <td>
                                <button onClick={() => makeEdit(item.workPlanId)}>Edit</button>
                                <button onClick={() => makeDelete(item.workPlanId)}>Delete</button>
                            </td>
                        </tr>
                    ))}
                    </tbody>
                </table>
            </div>
            <div className="home-page__button">
                <Link to="/home">Back</Link>
            </div>
        </section>
    )
}

export default EditWorkPlans
