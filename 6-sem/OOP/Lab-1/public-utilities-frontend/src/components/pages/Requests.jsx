import { Link } from "react-router-dom"
import "./Entity.css"
import "../Home.css"
import axios from "../../api/axios"
import {useEffect, useState} from "react"
import getHeaderConfig from "../hooks/Config"
const REQUEST_URL = "/request";

const Requests = () => {
    const [data, setData] = useState([]);
    const [id, setID] = useState('');

    const config = getHeaderConfig();

    const makeRequest = async (field, value) => {
        console.log("Making request");
        let url;
        if (field === 'all' && value === 'all') {
            url = `${REQUEST_URL}/all`;
        } else {
            url = `${REQUEST_URL}/?${field}=${value}`;
        }

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
    }

    useEffect(() => {
        makeRequest("all", "all");
    }, []);

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
                    </tr>
                    </thead>
                    <tbody>
                    {data?.map((item) => (
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
            <div className="home-page__button">
                <Link to="/view">Back</Link>
            </div>
        </section>
    )
}

export default Requests
