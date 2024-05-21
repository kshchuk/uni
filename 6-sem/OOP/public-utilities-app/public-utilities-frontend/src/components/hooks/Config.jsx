let token = ""

const getHeaderConfig = () => {
    return {
        headers: {
            'Content-Type': 'application/json',
            'access-token': token,
        }
    };
}

const setToken = (newToken) => {
    token = newToken;
}

export default getHeaderConfig;
export { setToken };