const getHeaderConfig = () => {
    const token = JSON.parse(window.localStorage.getItem("Token")).token;

    return {
        headers: {
            'Content-Type': 'application/json',
            'access-token': token
        }
    };
}

export default getHeaderConfig;