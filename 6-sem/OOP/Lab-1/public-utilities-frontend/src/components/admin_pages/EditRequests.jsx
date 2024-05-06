import { Link } from "react-router-dom"
import "../pages/Entity.css"
import "../Home.css"
import axios from "../../api/axios"
import {useEffect, useState} from "react"
import getHeaderConfig from "../hooks/Config"

const TENANT_URL = "/tenant"
const REQUEST_URL = "/request"

const EditRequests = async () => {

    const [data, setData] = useState([]);

    const [tenantId, setTenantId] = useState('');

    const [workType, setWorkType] = useState('');
    const [scopeOfWork, setScopeOfWork] = useState('');
    const [desiredTime, setDesiredTime] = useState('');

    const config = getHeaderConfig();

    const makeRequest = async (field, value) => {
        console.log("Making request");
        let url = `${TENANT_URL}/requests?${field}=${value}`;

        try {
            const response = await axios.get(url, {
                headers: config.headers
            });
            console.log(JSON.stringify(response.data));
            if (Array.isArray(response.data)) {
                setData(response.data);
            } else {
                setData([response.data]);
            }
        } catch (error) {
            console.error("Error making request:", error.message);
        }
    };

    const makeEdit = async (id) => {
        const editItem = data.find((item) => item.requestId === id);
        const response = await axios.put(REQUEST_URL, JSON.stringify(editItem), config);
        setData((prevData) => prevData.map(item => item.requestId === id ? response.data : item));
    };

    const makeDelete = async (id) => {
        let url = `${REQUEST_URL}/?${id}`;
        const response = await axios.delete(url, config);
        if (response.status !== 200) {
            console.error("Error deleting item");
            return;
        }
        setData((prevData) => prevData.filter(item => item.requestId !== id));
    };

    const makeCreate = async () => {
        const response = await axios.post(TENANT_URL, JSON.stringify({
            tenantId: tenantId,
            workType: workType,
            scopeOfWork: scopeOfWork,
            desiredTime: desiredTime
        }), config);
        setData((prevData) => [...prevData, response.data]);
        setTenantId("");
        setWorkType("");
        setScopeOfWork("");
        setDesiredTime("");
    };

    useEffect(() => {
        makeRequest("id", tenantId); // Fetch data when tenantId changes
    }, [tenantId]);

    return (
        <section>
            <h2>Requests</h2>
            <div className="queries">
                <div>
                    <label htmlFor="byID">Query by Tenant ID</label>
                    <input type="text" id="byID" onChange={(e) => setTenantId(e.target.value)} value={tenantId} />
                    <button onClick={() => makeRequest("id", tenantId)}>Execute Query</button>
                </div>
            </div>
            <p>You can edit data about requests</p>
            <div className="container">
                <h2>Data Table</h2>
                <table>
                    <thead>
                    <tr>
                        <th>Request ID</th>
                        <th>Work Type</th>
                        <th>Scope of Work</th>
                        <th>Desired Time</th>
                        <th>Actions</th>
                    </tr>
                    </thead>
                    <tbody>
                    <tr>
                        <td>Create new:</td>
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
                                <button onClick={() => makeDelete(item.requestId)}>Delete</button>
                            </td>
                        </tr>
                    ))}
                    </tbody>
                </table>
            </div>
            <div className="home-page__button">
                <Link to="/dispatch_view">Back</Link>
            </div>
        </section>
    )
}

export default EditRequests