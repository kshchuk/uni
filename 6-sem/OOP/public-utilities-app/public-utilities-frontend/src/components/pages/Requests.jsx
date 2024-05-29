import { Link } from "react-router-dom";
import "./Entity.css";
import "../Home.css";
import axios from "../../api/axios";
import { useState, useEffect } from "react";
import getHeaderConfig from "../hooks/Config";

const REQUEST_URL = "/request";
const TENANT_URL = "/tenant";

const Requests = () => {
    const [data, setData] = useState([]);
    const [id, setID] = useState('');
    const [tenant, setTenant] = useState({});
    const config = getHeaderConfig();
    const [requestCounts, setRequestCounts] = useState({});

    const makeRequest = async (endpoint) => {
        console.log("Making request");
        console.log(config.headers);
        const url = `${REQUEST_URL}/${endpoint}`;

        try {
            const response = await axios.get(url, { headers: config.headers });
            console.log(JSON.stringify(response.data));
            setData(response.data);
        } catch (error) {
            console.error("Error making request:", error.message);
        }
    };

    const getTenant = async (tenantId) => {
        console.log("Getting tenant");
        const url = `${TENANT_URL}/${tenantId}`;

        console.log(url);

        try {
            const response = await axios.get(url, { headers: config.headers });
            console.log(JSON.stringify(response.data));
            setTenant(response.data);
        } catch (error) {
            console.error("Error getting tenant:", error.message);
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

    useEffect(() => {
        makeRequest("all");
    }, []);

    useEffect(() => {
        if (tenant.id) {
            getRequestsCount(tenant.id);
        }
    }, [tenant]);

    const formatDuration = (duration) => {
        const { hours, minutes } = duration;
        return `${hours}h ${minutes}m`;
    };

    return (
        <section>
            <h2>Requests</h2>
            <p>You can query data about requests</p>
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
                    {data?.map((item) => (
                        <tr key={item.id}>
                            <td>{item.id}</td>
                            <td>{item.tenant.id}</td>
                            <td>{item.workType}</td>
                            <td>{item.scopeOfWork}</td>
                            <td>{formatDuration(item.desiredTime)}</td>
                            <td>
                                <button onClick={() => getTenant(item.tenant.id)}>Get Tenant</button>
                            </td>
                        </tr>
                    ))}
                    </tbody>
                </table>
            </div>
            <div className="queries">
                <div>
                    <label htmlFor="byID">Query by ID</label>
                    <input type="text" id="byID" onChange={(e) => setID(e.target.value)} value={id} />
                    <button onClick={() => makeRequest(id)}>Execute Query</button>
                </div>
                <div>
                    <label htmlFor="all">Query All</label>
                    <button onClick={() => makeRequest("all")}>All</button>
                </div>
            </div>
            <div className="home-page__button">
                <Link to="/">Back</Link>
            </div>
            <div className="container">
                <h2>Tenant Details</h2>
                <table>
                    <thead>
                    <tr>
                        <th>Tenant ID</th>
                        <th>Name</th>
                        <th>Address</th>
                        <th>Request IDs</th>
                    </tr>
                    </thead>
                    <tbody>
                    <tr>
                        <td>{tenant.id}</td>
                        <td>{tenant.name}</td>
                        <td>{tenant.address}</td>
                        <td>{requestCounts[tenant.id]}</td>
                    </tr>
                    </tbody>
                </table>
            </div>
        </section>
    );
};

export default Requests;
