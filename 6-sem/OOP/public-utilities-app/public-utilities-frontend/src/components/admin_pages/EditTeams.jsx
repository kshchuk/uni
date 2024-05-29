import { Link } from "react-router-dom";
import "../pages/Entity.css";
import "../Home.css";
import axios from "../../api/axios";
import { useEffect, useState } from "react";
import getHeaderConfig from "../hooks/Config";

const TEAM_URL = "/team";
const SPECIALIST_URL = "/specialist";
const WORKPLAN_URL = "/workplan";

const EditTeams = () => {
    const [data, setData] = useState([]);
    const [specialists, setSpecialists] = useState([]);
    const [workplans, setWorkplans] = useState([]);
    const [dispatcherId, setDispatcherId] = useState('');
    const [selectedAddSpecialistId, setSelectedAddSpecialistId] = useState('');
    const [selectedRemoveSpecialistId, setSelectedRemoveSpecialistId] = useState('');
    const [reload, setReload] = useState(false);

    const config = getHeaderConfig();

    const makeRequest = async (endpoint) => {
        console.log("Making request");
        const url = `${TEAM_URL}/${endpoint}`;
        try {
            const response = await axios.get(url, { headers: config.headers });
            console.log(JSON.stringify(response.data));
            setData(response.data);
        } catch (error) {
            console.error("Error making request:", error.message);
        }
    };

    const fetchSpecialists = async () => {
        const url = `${SPECIALIST_URL}/all`;
        try {
            const response = await axios.get(url, { headers: config.headers });
            console.log(JSON.stringify(response.data));
            setSpecialists(Array.isArray(response.data) ? response.data : [response.data]);
        } catch (error) {
            console.error("Error fetching specialists:", error.message);
        }
    };

    const getWorkPlans = async (id) => {
        console.log("Getting work plans");
        const url = `${WORKPLAN_URL}/team/${id}`;
        try {
            const response = await axios.get(url, { headers: config.headers });
            console.log(JSON.stringify(response.data));
            setWorkplans(Array.isArray(response.data) ? response.data : [response.data]);
        } catch (error) {
            console.error("Error getting work plans:", error.message);
        }
    };

    const makeDelete = async (id) => {
        const url = `${TEAM_URL}/${id}`;
        const response = await axios.delete(url, config);
        if (response.status !== 200) {
            console.error("Error deleting item");
            return;
        }
        setData((prevData) => prevData.filter(item => item.id !== id));
    };

    const makeCreate = async () => {
        if (!dispatcherId) {
            console.error("Dispatcher ID must be set");
            return;
        }
        const url = `${TEAM_URL}/create`;
        await axios.post(url, JSON.stringify({ dispatcherId, specialistIds: [], workPlanIds: [] }), config);
        makeRequest("all");
    };

    const addSpecialist = async (id) => {
        const team = data.find((item) => item.id === id);
        if (!team.specialistIds.includes(selectedAddSpecialistId)) {
            team.specialistIds.push(selectedAddSpecialistId);
            await axios.put(TEAM_URL, JSON.stringify(team), config);
        }
        setReload(!reload);
    };

    const removeSpecialist = async (id) => {
        const team = data.find((item) => item.id === id);
        team.specialistIds = team.specialistIds.filter(sid => sid !== selectedRemoveSpecialistId);
        await axios.put(TEAM_URL, JSON.stringify(team), config);
        setReload(!reload);
    };

    useEffect(() => {
        makeRequest("all");
        fetchSpecialists();
    }, [reload]);

    return (
        <section>
            <h2>Teams</h2>
            <p>You can edit data about teams</p>
            <div className="container">
                <h2>Data Table</h2>
                <table>
                    <thead>
                    <tr>
                        <th>Team ID</th>
                        <th>Dispatcher ID</th>
                        <th>Specialist IDs</th>
                        <th>Work Plan IDs</th>
                        <th>Actions</th>
                    </tr>
                    </thead>
                    <tbody>
                    <tr>
                        <td>Create new:</td>
                        <td>
                            <input type="text" onChange={(e) => setDispatcherId(e.target.value.trimEnd())} />
                        </td>
                        <td></td>
                        <td></td>
                        <td><button onClick={makeCreate}>Create</button></td>
                    </tr>
                    {data && data.map((item) => (
                        <tr key={item.id}>
                            <td>{item.id}</td>
                            <td>{item.dispatcherId}</td>
                            <td>
                                {item.specialistIds && item.specialistIds.map((id) => {
                                    const specialist = specialists.find(spec => spec.specialistId === id);
                                    return specialist ? <p key={id}>{specialist.name}</p> : null;
                                })}
                                <div>
                                    <label>Add Specialist</label>
                                    <select onChange={(e) => setSelectedAddSpecialistId(e.target.value)}>
                                        {specialists.map((specialist) => (
                                            <option key={specialist.specialistId} value={specialist.specialistId}>
                                                {specialist.name}
                                            </option>
                                        ))}
                                    </select>
                                    <button onClick={() => addSpecialist(item.id)}>Add</button>
                                </div>
                                <div>
                                    <label>Remove Specialist</label>
                                    <select onChange={(e) => setSelectedRemoveSpecialistId(e.target.value)}>
                                        {item.specialistIds && item.specialistIds.map((id) => {
                                            const specialist = specialists.find(spec => spec.specialistId === id);
                                            return specialist ? (
                                                <option key={id} value={specialist.specialistId}>
                                                    {specialist.name}
                                                </option>
                                            ) : null;
                                        })}
                                    </select>
                                    <button onClick={() => removeSpecialist(item.id)}>Remove</button>
                                </div>
                            </td>
                            <td>{item.workPlanIds ? item.workPlanIds.length : 0}</td>
                            <td>
                                <button onClick={() => makeDelete(item.id)}>Delete</button>
                                <button onClick={() => getWorkPlans(item.id)}>Get Work Plans</button>
                            </td>
                        </tr>
                    ))}
                    </tbody>
                </table>
            </div>
            <div className="home-page__button">
                <Link to="/home">Back</Link>
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
                    {workplans && workplans.map((item, index) => (
                        <tr key={index}>
                            <td>{item.id}</td>
                            <td>{item.description}</td>
                            <td>{item.duration}</td>
                            <td>{item.team.id}</td>
                        </tr>
                    ))}
                    </tbody>
                </table>
            </div>
        </section>
    );
};

export default EditTeams;
