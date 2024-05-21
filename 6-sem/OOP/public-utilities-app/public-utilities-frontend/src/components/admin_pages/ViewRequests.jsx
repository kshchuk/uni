import { Link } from "react-router-dom"
import "../pages/Entity.css"
import "../Home.css"
import axios from "../../api/axios"
import {useEffect, useState} from "react"
import getHeaderConfig from "../hooks/Config"

const REQUEST_URL = "/request"

const ViewRequests = () => {
    const [data, setData] = useState([]);

    const [workType, setWorkType] = useState('');
    const [scopeOfWork, setScopeOfWork] = useState('');
    const [desiredTime, setDesiredTime] = useState('');

    const config = getHeaderConfig();

    const makeRequest = async (field, value) => {
        console.log("Making request");
        let url;
        if (field === 'all' && value === 'all') {
            url = `${REQUEST_URL}/all`;
        } else {
            url = `${REQUEST_URL}?${field}=${value}`;
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

    const makeEdit = async (id) => {
        const editItem = data.find((item) => item.requestId === id);
        const response = await axios.put(REQUEST_URL, JSON.stringify({
            requestId: editItem.requestId,
            tenantId: editItem.tenantId,
            workType: editItem.workType,
            scopeOfWork: editItem.scopeOfWork,
            desiredTime: editItem.desiredTime
        }), config);
    };

    const makeDelete = async (id) => {
        let url = `${REQUEST_URL}/?id=${id}`;
        const response = await axios.delete(url, config);
        if (response.status !== 200) {
            console.error("Error deleting item");
            return;
        }
        setData((prevData) => prevData.filter(item => item.requestId !== id));
    };

    useEffect(() => {
        makeRequest("all", "all"); // Fetch data when page loads
    }, []);

    return (
        <section>
            <h2>Requests</h2>
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
                <Link to="/home">Back</Link>
            </div>
        </section>
    )
}

export default ViewRequests
