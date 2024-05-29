import { Link } from "react-router-dom";
import "./Entity.css";
import "../Home.css";
import axios from "../../api/axios";
import { useState, useEffect } from "react";
import getHeaderConfig from "../hooks/Config";

const TENANT_URL = "/tenant";
const REQUEST_URL = "/request";

const Tenants = () => {
    const [data, setData] = useState([]);
    const [id, setID] = useState('');
    const [requests, setRequests] = useState([]);
    const [requestCounts, setRequestCounts] = useState({});
    const config = getHeaderConfig();

    const makeRequest = async (endpoint) => {
        console.log("Making request");
        console.log(config.headers);
        const url = `${TENANT_URL}/${endpoint}`;

        try {
            const response = await axios.get(url, { headers: config.headers });
            console.log(JSON.stringify(response.data));
            setData(response.data);
        } catch (error) {
            console.error("Error making request:", error.message);
        }
    };

    const getRequests = async (tenantId) => {
        const url = `${REQUEST_URL}/tenant/${tenantId}`;

        try {
            const response = await axios.get(url, { headers: config.headers });
            if (!response?.data) {
                console.error("Error getting requests");
                return;
            }
            console.log(JSON.stringify(response.data));
            setRequests(response.data);
        } catch (error) {
            console.error("Error getting requests:", error.message);
        }
    };

    const getRequestsCount = async (tenantId) => {
        const url = `${REQUEST_URL}/tenant/${tenantId}/count`;

        try {
            const response = await axios.get(url, {headers: config.headers});
            if (!response?.data) {
                console.error("Error getting requests count");
                return;
            }
            console.log(JSON.stringify(response.data));
            setRequestCounts(prevCounts => ({...prevCounts, [tenantId]: response.data}));
        } catch (error) {
            console.error("Error getting requests count:", error.message);
        }
    }

    const formatDuration = (duration) => {
        const { hours, minutes } = duration;
        return `${hours}h ${minutes}m`;
    };

    useEffect(() => {
        makeRequest("all");
        data.forEach(item => {
            getRequestsCount(item.id);
        });
    }, [data]);

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
                    {data.map((item) => (
                        <tr key={item.id}>
                            <td>{item.id}</td>
                            <td>{item.name}</td>
                            <td>{item.address}</td>
                            <td>{requestCounts[item.id] || 0}</td>
                            <td>
                                <button onClick={() => getRequests(item.id)}>Get Requests</button>
                            </td>
                        </tr>
                    ))}
                    </tbody>
                </table>
            </div>
            <div className="queries">
                <div>
                    <label htmlFor="byID">Query by ID</label>
                    <input
                        type="text"
                        id="byID"
                        onChange={(e) => setID(e.target.value)}
                        value={id}
                    />
                    <button onClick={() => makeRequest(id)}>Execute Query</button>
                </div>
            </div>
            <div className="home-page__button">
                <Link to="/">Back</Link>
            </div>
            <div className="container">
                <h2>Tenant Requests</h2>
                <table>
                    <thead>
                    <tr>
                        <th>Request ID</th>
                        <th>Tenant ID</th>
                        <th>Work Type</th>
                        <th>Scope of Work</th>
                        <th>Desired Time</th>
                    </tr>
                    </thead>
                    <tbody>
                    {requests.map((item) => (
                        <tr key={item.id}>
                            <td>{item.id}</td>
                            <td>{item.tenant.id}</td>
                            <td>{item.workType}</td>
                            <td>{item.scopeOfWork}</td>
                            <td>{formatDuration(item.desiredTime)}</td>
                        </tr>
                    ))}
                    </tbody>
                </table>
            </div>
        </section>
    );
};

export default Tenants;
