import { Link } from "react-router-dom";
import "../pages/Entity.css";
import "../Home.css";
import axios from "../../api/axios";
import { useEffect, useState } from "react";
import getHeaderConfig from "../hooks/Config";

const WORKPLAN_URL = "/work-plan";
const TEAM_URL = "/team";

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
            const response = await axios.get(url, { headers: config.headers });
            console.log(JSON.stringify(response.data));
            setData(Array.isArray(response.data) ? response.data : [response.data]);
        } catch (error) {
            console.error("Error making request:", error.message);
        }
    };

    const fetchTeams = async () => {
        const url = `${TEAM_URL}/all`;

        try {
            const response = await axios.get(url, { headers: config.headers });
            console.log(JSON.stringify(response.data));
            setTeams(Array.isArray(response.data) ? response.data : [response.data]);
        } catch (error) {
            console.error("Error fetching teams:", error.message);
        }
    };

    const makeEdit = async (id) => {
        const editItem = data.find((item) => item.id === id);
        try {
            await axios.put(WORKPLAN_URL, JSON.stringify({
                id: editItem.id,
                description: editItem.description,
                duration: editItem.duration,
                teamId: editItem.teamId
            }), config);
        } catch (error) {
            console.error("Error editing item:", error.message);
        }
    };

    const makeDelete = async (id) => {
        const url = `${WORKPLAN_URL}/?id=${id}`;
        try {
            const response = await axios.delete(url, config);
            if (response.status === 200) {
                setData((prevData) => prevData.filter(item => item.id !== id));
            } else {
                console.error("Error deleting item");
            }
        } catch (error) {
            console.error("Error deleting item:", error.message);
        }
    };

    const makeCreate = async () => {
        try {
            await axios.post(WORKPLAN_URL, JSON.stringify({
                description: description,
                duration: duration,
                teamId: selectedTeamId
            }), config);
            setDescription("");
            setDuration("");
            setSelectedTeamId("");
            makeRequest("all", "all");
        } catch (error) {
            console.error("Error creating item:", error.message);
        }
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
                        <td>
                            <select onChange={(e) => setSelectedTeamId(e.target.value)} value={selectedTeamId}>
                                {teams.map((team) => (
                                    <option key={team.teamId} value={team.teamId}>{team.teamId}</option>
                                ))}
                            </select>
                        </td>
                        <td><button onClick={makeCreate}>Create</button></td>
                    </tr>
                    {data && data.map((item) => (
                        <tr key={item.id}>
                            <td>{item.id}</td>
                            <td>
                                <input
                                    type="text"
                                    value={item.description}
                                    onChange={(e) => {
                                        const newData = data.map(el =>
                                            el.id === item.id ? { ...el, description: e.target.value } : el
                                        );
                                        setData(newData);
                                    }}
                                />
                            </td>
                            <td>
                                <input
                                    type="text"
                                    value={item.duration}
                                    onChange={(e) => {
                                        const newData = data.map(el =>
                                            el.id === item.id ? { ...el, duration: e.target.value } : el
                                        );
                                        setData(newData);
                                    }}
                                />
                            </td>
                            <td>
                                <input
                                    type="text"
                                    value={item.teamId}
                                    onChange={(e) => {
                                        const newData = data.map(el =>
                                            el.id === item.id ? { ...el, teamId: e.target.value } : el
                                        );
                                        setData(newData);
                                    }}
                                />
                            </td>
                            <td>
                                <button onClick={() => makeEdit(item.id)}>Edit</button>
                                <button onClick={() => makeDelete(item.id)}>Delete</button>
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
    );
};

export default EditWorkPlans;
