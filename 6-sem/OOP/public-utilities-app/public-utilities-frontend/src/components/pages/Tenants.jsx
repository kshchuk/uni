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
        console.log("Making request");
        let url;
        if (field === 'all' && value === 'all') {
            url = `${TENANT_URL}/all`;
        } else {
            url = `${TENANT_URL}/?${field}=${value}`;
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

    // format time to hour minute (for ex PT32H is 32 hours, PT1H30M is 1 hour 30 minutes
    const formatDuration = (time) => {
        let hours = 0;
        let minutes = 0;
        if (time.includes("H")) {
            hours = parseInt(time.split("H")[0].substring(2));
        }
        if (time.includes("M")) {
            minutes = parseInt(time.split("M")[0].split("H")[1].substring(2));
        }
        let result = "";
        if (hours > 0) {
            result += hours + " hours ";
        }
        if (minutes > 0) {
            result += minutes + " minutes";
        }
        return result;
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
                        <tr key={item.tenantId}>
                            <td>{item.tenantId}</td>
                            <td>{item.name}</td>
                            <td>{item.address}</td>
                            <td>{item.requestIds ? item.requestIds.length : 0}</td>
                            <td>
                                <button onClick={() => getRequests(item.tenantId)}>Get Requests</button>
                            </td>
                        </tr>
                    ))}
                    </tbody>
                </table>
            </div>
            <div className="queries">
                <div>
                    <label htmlFor="byID">Query by ID</label>
                    <input type="text" id="byID" onChange={(e) => setID(e.target.value)} value={id}/>
                    <button onClick={() => makeRequest("id", id)}>Execute Query</button>
                </div>
            </div>
            <div className="home-page__button">
                <Link to="/view">Back</Link>
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
                    {requests?.map((item) => (
                        <tr key={item.id}>
                            <td>{item.requestId}</td>
                            <td>{item.tenantId}</td>
                            <td>{item.workType}</td>
                            <td>{item.scopeOfWork}</td>
                            <td>{formatDuration(item.desiredTime)}</td>
                        </tr>
                    ))}
                    </tbody>
                </table>
            </div>
        </section>
    )
}

export default Tenants
