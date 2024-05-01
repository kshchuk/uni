import { Link } from "react-router-dom"
import "../pages/Entity.css"
import "../Home.css"
import axios from "../../api/axios"
import { useState } from "react"
import getHeaderConfig from "../hooks/Config"

const SET_URL = "/team"

const CreateTeam = () => {

    const [data, setData] = useState([]);
    const [id, setID] = useState('');
    const [specialistIds, setSpecialistIds] = useState([]);

    const [dispatcherId, setDispatcherId] = useState('');
    const [specialistId, setSpecialistId] = useState('');

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
        getIds();
    }

    const getIds = async() => {
        const specialistIdsResp = await axios.get(SET_URL, {
            params: {
                field: "specialists",
                value: "specialists"
            },
            headers: config.headers
        });
        console.log(JSON.stringify(specialistIdsResp?.data));
        setSpecialistIds(specialistIdsResp?.data);
    }

    const makeEdit = async (id) => {
        const editItem = data.find((item) => item.teamId === id);
        const response = await axios.put(SET_URL, JSON.stringify(editItem), config);
        setData(response?.data);
        getIds();
    }

    const makeDelete = async (field, value) => {
        const response = await axios.get(SET_URL, {
            params: {
                field: field,
                value: value
            },
            headers: config.headers
        });
        setData(response?.data);
        getIds()
    }

    const makeCreate = async () => {
        const response = await axios.post(SET_URL, JSON.stringify({
            teamId: "",
            dispatcherId: dispatcherId,
            specialistIds: [specialistId],
            workPlanIds: []
        }), config);
        setData(response?.data);
        setDispatcherId("");
        setSpecialistId("");
        getIds();
    }

    return (
        <section>
            <h2>Teams</h2>
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
                        <td><input type="text" onChange={(e) => setDispatcherId(e.target.value)} value={dispatcherId}></input></td>
                        <td><input type="text" onChange={(e) => setSpecialistId(e.target.value)} value={specialistId}></input></td>
                        <td></td>
                        <td><button onClick={makeCreate}>Create</button></td>
                    </tr>
                    {data?.map((item) => (
                        <tr key={item.teamId}>
                            <td>{item.teamId}</td>
                            <td><input type="text" value={item.dispatcherId} onChange={(e) => {
                                const newData = [...data];
                                newData.find((el) => el.teamId === item.teamId).dispatcherId = e.target.value;
                                setData(newData);
                            }}/></td>
                            <td><input type="text" value={item.specialistIds.join(", ")} onChange={(e) => {
                                const newData = [...data];
                                newData.find((el) => el.teamId === item.teamId).specialistIds = e.target.value.split(", ");
                                setData(newData);
                            }}/></td>
                            <td>{item.workPlanIds.join(", ")}</td>
                            <td>
                                <button onClick={() => makeEdit(item.teamId)}>Edit</button>
                                <button onClick={() => makeDelete("delete", item.teamId)}>Delete</button>
                            </td>
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

export default CreateTeam
