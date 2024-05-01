import { Link } from "react-router-dom"
import "./Entity.css"
import "../Home.css"
import axios from "../../api/axios"
import { useState, useEffect } from "react"
import getHeaderConfig from "../hooks/Config"
const TENANT_URL = "/tenant";

const Tenants = () => {
    const [data, setData] = useState([]);
    const [id, setID] = useState('');
    const [requests, setRequests] = useState([]);

    const config = getHeaderConfig();

    const makeRequest = async (field, value) => {
        const response = await axios.get(TENANT_URL, {
            params: {
                field: field,
                value: value
            },
            headers: config.headers
        });
        console.log(JSON.stringify(response?.data));
        setData(response?.data);
    }

    const getRequests = async (tenantId) => {
        const response = await axios.get(`${TENANT_URL}/requests`, {
            params: {
                id: tenantId
            },
            headers: config.headers
        });
        console.log(JSON.stringify(response?.data));
        setRequests(response?.data);
    }

    useEffect(() => {
        makeRequest("all", "all");
    }, []);

    return (
        <section>
            <h2>Tenants</h2>
            <p>You can query data about tenants</p>
            <div className="container">
                <h2>Data Table</h2>
                <table>
                    <thead>
                    <tr>
                        <th>Tenant ID</th>
                        <th>Name</th>
                        <th>Address</th>
                        <th>Request IDs</th>
                        <th>Actions</th>
                    </tr>
                    </thead>
                    <tbody>
                    {data?.map((item) => (
                        <tr key={item.id}>
                            <td>{item.id}</td>
                            <td>{item.name}</td>
                            <td>{item.address}</td>
                            <td>{item.requestIds.join(", ")}</td>
                            <td><button onClick={() => getRequests(item.tenantId)}>Get Requests</button></td>
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
                <h2>Requests</h2>
                <ul>
                    {requests?.map((request, index) => (
                        <li key={index}>{request.requestId}: {request.workType}, {request.scopeOfWork}, {request.desiredTime}</li>
                    ))}
                </ul>
            </div>
        </section>
    )
}

export default Tenants
