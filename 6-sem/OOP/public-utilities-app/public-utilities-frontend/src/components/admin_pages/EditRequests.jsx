import { Link } from "react-router-dom";
import "../pages/Entity.css";
import "../Home.css";
import axios from "../../api/axios";
import { useEffect, useState } from "react";
import getHeaderConfig from "../hooks/Config";

const REQUEST_URL = "/request";
const TENANT_URL = "/tenant";

const EditRequests = () => {
    const [data, setData] = useState([]);

    const [workType, setWorkType] = useState('');
    const [scopeOfWork, setScopeOfWork] = useState('');
    const [desiredTime, setDesiredTime] = useState('');

    const [tenants, setTenants] = useState({});
    const [tenant, setTenant] = useState('');

    const config = getHeaderConfig();

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

    const makeEdit = async (id) => {
        const editItem = data.find((item) => item.id === id);
        let url = `${REQUEST_URL}/update`;

        const response = await axios.put(url, JSON.stringify({
            id: editItem.id,
            tenant: editItem.tenant,
            workType: editItem.workType,
            scopeOfWork: editItem.scopeOfWork,
            desiredTime: fromTextToDuration(editItem.desiredTime)
        }), config);
        if (response.status !== 200) {
            console.error("Error updating item");
        } else {
            console.log("Item updated:", response.data);
        }
    };

    const makeDelete = async (id) => {
        let url = `${REQUEST_URL}/${id}`;
        const response = await axios.delete(url, config);
        if (response.status !== 200) {
            console.error("Error deleting item");
            return;
        }
        setData((prevData) => prevData.filter(item => item.id !== id));
    };

    const makeCreate = async () => {
        let url = `${REQUEST_URL}/create`;

        const response = await axios.post(url, JSON.stringify({
            tenant: tenant,
            workType: workType,
            scopeOfWork: scopeOfWork,
            desiredTime: fromTextToDuration(desiredTime)
        }), config);
        setWorkType("");
        setScopeOfWork("");
        setDesiredTime("");

        if (response.status !== 200) {
            console.error("Error creating item");
        } else {
            console.log("Item created:", response.data);
            setData((prevData) => [...prevData, response.data]);
        }
    };

    const fromDurationToText = (duration) => {
        const { hours, minutes } = duration;
        return `${hours}h ${minutes}m`;
    };

    const fromTextToDuration = (text) => {
        const [hours, minutes] = text.split("h").map(part => part.trim().replace('m', ''));
        return {
            type: "interval",
            value: `0 years 0 mons 0 days ${hours} hours ${minutes} mins 0.0 secs`,
            years: 0,
            months: 0,
            days: 0,
            hours: parseInt(hours),
            minutes: parseInt(minutes),
            wholeSeconds: 0,
            microSeconds: 0,
            seconds: 0,
            null: false
        };
    };

    const loadTenants = async () => {
        const url = `${TENANT_URL}/all`;

        try {
            const response = await axios.get(url, { headers: config.headers });
            console.log(JSON.stringify(response.data));
            setTenants(response.data);
            setTenant(response.data[0]);
        } catch (error) {
            console.error("Error getting tenant:", error.message);
        }
    };

    useEffect(() => {
        makeRequest("all");
        loadTenants();
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
                    <tr>
                        <td>Create new:</td>
                        <td><input type="text" onChange={(e) => setWorkType(e.target.value)} value={workType}></input></td>
                        <td><input type="text" onChange={(e) => setScopeOfWork(e.target.value)} value={scopeOfWork}></input></td>
                        <td><input type="text" onChange={(e) => setDesiredTime(e.target.value)} value={desiredTime}></input></td>
                        <td><button onClick={makeCreate}>Create</button></td>
                    </tr>
                    {data?.map((item) => (
                        <tr key={item.id}>
                            <td>{item.id}</td>
                            <td><input
                                type="text"
                                value={item.workType}
                                onChange={(e) => {
                                    const newData = [...data];
                                    newData.find((el) => el.id === item.id).workType = e.target.value;
                                    setData(newData);
                                }}
                            /></td>
                            <td><input
                                type="text"
                                value={item.scopeOfWork}
                                onChange={(e) => {
                                    const newData = [...data];
                                    newData.find((el) => el.id === item.id).scopeOfWork = e.target.value;
                                    setData(newData);
                                }}
                            /></td>
                            <td><input
                                type="text"
                                value={fromDurationToText(item.desiredTime)}
                                onChange={(e) => {
                                    const newData = [...data];
                                    newData.find((el) => el.id === item.id).desiredTime = e.target.value;
                                    setData(newData);
                                }}
                            /></td>
                            <td>
                                <button onClick={() => makeEdit(item.id)}>Edit</button>
                                <button onClick={() => makeDelete(item.id)}>Delete</button>
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

export default EditRequests;
