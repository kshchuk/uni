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
    const [selectedSpecialistId, setSelectedSpecialistId] = useState('');

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
    };

    const makeEdit = async (id) => {
        const editItem = data.find((item) => item.teamId === id);
        const response = await axios.put(TEAM_URL, JSON.stringify(editItem), config);
    };

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
        const response = await axios.post(TEAM_URL, JSON.stringify({
            dispatcherId: dispatcherId,
            specialistIds: [],
            workPlanIds: []
        }), config);
        makeRequest("all", "all");
    };

    const addSpecialist = async (teamId) => {
        const team = data.find((item) => item.teamId === teamId);
        if (!team.specialistIds.includes(selectedSpecialistId)) {
            team.specialistIds.push(selectedSpecialistId);
            const response = await axios.put(TEAM_URL, JSON.stringify(team), config);
            // Update the specialist's teamId
            const specialist = specialists.find((item) => item.specialistId === selectedSpecialistId);
            specialist.teamId = teamId;
            await axios.put(SPECIALIST_URL, JSON.stringify(specialist), config);
        }
    };

    const removeSpecialist = async (teamId, specialistId) => {
        const team = data.find((item) => item.teamId === teamId);
        team.specialistIds = team.specialistIds.filter(id => id !== specialistId);
        const response = await axios.put(TEAM_URL, JSON.stringify(team), config);
        // Update the specialist's teamId
        const specialist = specialists.find((item) => item.specialistId === specialistId);
        specialist.teamId = null;
        await axios.put(SPECIALIST_URL, JSON.stringify(specialist), config);
    };

    useEffect(() => {
        makeRequest("all", "all"); // Fetch data when page loads
        fetchSpecialists(); // Fetch specialists when page loads
    }, []);

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
                        <td>{dispatcherId}</td>
                        <td><select onChange={(e) => setSelectedSpecialistId(e.target.value)}>
                            {specialists.map((specialist) => (
                                <option value={specialist.specialistId}>{specialist.name}</option>
                            ))}
                        </select></td>
                        <td><button onClick={() => makeCreate()}>Create</button></td>
                    </tr>
                    {data?.map((item) => (
                        <tr key={item.teamId}>
                            <td>{item.teamId}</td>
                            <td>{item.dispatcherId}</td>
                            <td>{item.specialistIds.join(", ")}</td>
                            <td>
                                <button onClick={() => makeEdit(item.teamId)}>Edit</button>
                                <button onClick={() => makeDelete(item.teamId)}>Delete</button>
                                <button onClick={() => addSpecialist(item.teamId)}>Add Specialist</button>
                                <button onClick={() => removeSpecialist(item.teamId, selectedSpecialistId)}>Remove Specialist</button>
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
