import { Link } from "react-router-dom"
import "../pages/Entity.css"
import "../Home.css"
import axios from "../../api/axios"
import { useState } from "react"
import getHeaderConfig from "../hooks/Config"

const SET_URL = "/request"

const EditRequest = () => {

    const [data, setData] = useState([]);
    const [id, setID] = useState('');

    const [tenantId, setTenantId] = useState('');
    const [workType, setWorkType] = useState('');
    const [scopeOfWork, setScopeOfWork] = useState('');
    const [desiredTime, setDesiredTime] = useState('');

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

    const makeEdit = async (id) => {
        const editItem = data.find((item) => item.requestId === id);
        const response = await axios.put(SET_URL, JSON.stringify(editItem), config);
        setData(response?.data);
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
    }

    const makeCreate = async () => {
        const response = await axios.post(SET_URL, JSON.stringify({
            requestId: "",
            tenantId: tenantId,
            workType: workType,
            scopeOfWork: scopeOfWork,
            desiredTime: desiredTime
        }), config);
        setData(response?.data);
        setTenantId("");
        setWorkType("");
        setScopeOfWork("");
        setDesiredTime("");
    }

    return (
        <section>
            <h2>Requests</h2>
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
            <p>You can edit data about requests</p>
            <div className="container">
                <h2>Data Table</h2>
                <table>
                    <thead>
                    <tr>
                        <th>Request ID</th>
                        <th>Tenant ID</th>
                        <th>Work Type</th>
                        <th>Scope of Work</th>
                        <th>Desired Time</th>
                        <th>Actions</th>
                    </tr>
                    </thead>
                    <tbody>
                    <tr>
                        <td>Create new:</td>
                        <td><input type="text" onChange={(e) => setTenantId(e.target.value)} value={tenantId}></input></td>
                        <td><input type="text" onChange={(e) => setWorkType(e.target.value)} value={workType}></input></td>
                        <td><input type="text" onChange={(e) => setScopeOfWork(e.target.value)} value={scopeOfWork}></input></td>
                        <td><input type="text" onChange={(e) => setDesiredTime(e.target.value)} value={desiredTime}></input></td>
                        <td><button onClick={() => makeCreate()}>Create</button></td>
                    </tr>
                    {data?.map((item) => (
                        <tr key={item.requestId}>
                            <td>{item.requestId}</td>
                            <td><input
                                type="text"
                                value={item.tenantId}
                                onChange={(e) => {
                                    const newData = [...data];
                                    newData.find((el) => el.requestId === item.requestId).tenantId = e.target.value;
                                    setData(newData);
                                }}
                            /></td>
                            <td><input
                                type="text"
                                value={item.workType}
                                onChange={(e) => {
                                    const newData = [...data];
                                    newData.find((el) => el.requestId === item.requestId).workType = e.target.value;
                                    setData(newData);
                                }}
                            /></td>
                            <td><input
                                type="text"
                                value={item.scopeOfWork}
                                onChange={(e) => {
                                    const newData = [...data];
                                    newData.find((el) => el.requestId === item.requestId).scopeOfWork = e.target.value;
                                    setData(newData);
                                }}
                            /></td>
                            <td><input
                                type="text"
                                value={item.desiredTime}
                                onChange={(e) => {
                                    const newData = [...data];
                                    newData.find((el) => el.requestId === item.requestId).desiredTime = e.target.value;
                                    setData(newData);
                                }}
                            /></td>
                            <td>
                                <button onClick={() => makeEdit(item.requestId)}>Edit</button>
                                <button onClick={() => makeDelete("delete", item.requestId)}>Delete</button>
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

export default EditRequest
