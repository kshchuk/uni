import { Link } from "react-router-dom"
import "../pages/Entity.css"
import "../Home.css"
import axios from "../../api/axios"
import {useEffect, useState} from "react"
import getHeaderConfig from "../hooks/Config"

const TEAM_URL = "/team"
const SPECIALIST_URL = "/specialist"

const EditTeams = () => {
    const [data, setData] = useState([]);
    const [specialists, setSpecialists] = useState([]);

    const [dispatcherId, setDispatcherId] = useState('');
    const [selectedAddSpecialistId, setSelectedAddSpecialistId] = useState('');
    const [selectedRemoveSpecialistId, setSelectedRemoveSpecialistId] = useState('');

    const [reload, setReload] = useState(false);

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

    const fetchSpecialists = async () => {
        let url = `${SPECIALIST_URL}/all`;

        try {
            const response = await axios.get(url, {
                headers: config.headers
            });
            console.log(JSON.stringify(response.data));
            if (Array.isArray(response.data)) {
                setSpecialists(response.data);
            } else {
                setSpecialists([response.data]);
            }
        } catch (error) {
            console.error("Error fetching specialists:", error.message);
        }
    }

    const makeDelete = async (id) => {
        let url = `${TEAM_URL}/?id=${id}`;
        const response = await axios.delete(url, config);
        if (response.status !== 200) {
            console.error("Error deleting item");
            return;
        }
        setData((prevData) => prevData.filter(item => item.teamId !== id));
    };

    const makeCreate = async () => {
        if (dispatcherId === '') {
            console.error("Dispatcher ID must be set");
            return;
        }

        await axios.post(TEAM_URL, JSON.stringify({
            dispatcherId: dispatcherId,
            specialistIds: [],
            workPlanIds: []
        }), config);
        makeRequest("all", "all");
    };

    const addSpecialist = async (teamId) => {
        const team = data.find((item) => item.teamId === teamId);
        if (!team.specialistIds.includes(selectedAddSpecialistId)) {
            team.specialistIds.push(selectedAddSpecialistId);
            const response = await axios.put(TEAM_URL, JSON.stringify({
                teamId: team.teamId,
                dispatcherId: team.dispatcherId,
                specialistIds: team.specialistIds,
                workPlanIds: team.workPlanIds
            }), config);
        }

        setReload(!reload)
    };

    const removeSpecialist = async (teamId) => {
        const team = data.find((item) => item.teamId === teamId);
        if (selectedRemoveSpecialistId.length === 0 || selectedRemoveSpecialistId.length === 1) {
            setSelectedRemoveSpecialistId(team.specialistIds[0]);
        }
        team.specialistIds = team.specialistIds.filter(id => id !== selectedRemoveSpecialistId);
        const response = await axios.put(TEAM_URL, JSON.stringify({
            teamId: team.teamId,
            dispatcherId: team.dispatcherId,
            specialistIds: team.specialistIds,
            workPlanIds: team.workPlanIds
        }), config);

        setReload(!reload)
    };

    useEffect(() => {
        makeRequest("all", "all"); // Fetch data when page loads
        fetchSpecialists(); // Fetch specialists when page loads
    }, [reload]);

    return (
        <section>
            <h2>Teams</h2>
            <div className="queries">
                <div>
                    <label htmlFor="byID">Set Dispatcher ID</label>
                    <input type="text" id="byID" onChange={(e) => setDispatcherId(e.target.value.trimEnd())} />
                </div>
            </div>
            <p>You can edit data about teams</p>
            <div className="container">
                <h2>Data Table</h2>
                <table>
                    <thead>
                    <tr>
                        <th>Team ID</th>
                        <th>Dispatcher ID</th>
                        <th>Specialist IDs</th>
                        <th>Actions</th>
                    </tr>
                    </thead>
                    <tbody>
                    <tr>
                        <td>Create new:</td>
                        <td></td>
                        <td></td>
                        <td><button onClick={() => makeCreate()}>Create</button></td>
                    </tr>
                    {data?.map((item) => (
                        <tr key={item.teamId}>
                            <td>{item.teamId}</td>
                            <td>{item.dispatcherId}</td>
                            <td>
                                {item.specialistIds.map((id) => (
                                    specialists.map((specialist) => {
                                        if (specialist.specialistId === id) {
                                            return <p>{specialist.name}</p>
                                        }
                                    }
                                )))}
                                <div>
                                    <div>
                                    <label htmlFor="add">Add Specialist</label>
                                    <select onChange={(e) => setSelectedAddSpecialistId(e.target.value)}>
                                        {specialists.map((specialist) => (
                                            <option value={specialist.specialistId}>{specialist.name}</option>
                                        ))}
                                    </select>
                                    <button onClick={() => addSpecialist(item.teamId)}>Add Specialist</button>
                                        </div>
                                    <div>
                                    <label htmlFor="remove">Remove Specialist</label>
                                    <select onChange={(e) => setSelectedRemoveSpecialistId(e.target.value)}>
                                        {
                                            item.specialistIds.map((id) => (
                                                specialists.map((specialist) => {
                                                    if (specialist.specialistId === id) {
                                                        return <option value={specialist.specialistId}>{specialist.name}</option>
                                                    }
                                                }
                                            ))
                                        )}
                                    </select>
                                    <button
                                        onClick={() => removeSpecialist(item.teamId)}>Remove
                                        Specialist
                                    </button>
                                    </div>
                                </div>
                            </td>
                            <td>
                                <button onClick={() => makeDelete(item.teamId)}>Delete</button>
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

export default EditTeams