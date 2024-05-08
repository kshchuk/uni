import {useContext, useEffect} from 'react';
import AuthContext from './context/AuthProvider';

function Login() {
    const auth = useContext(AuthContext);

    useEffect(() => {
        if (!auth.isAuthenticated) {
            auth.login();
        }
    }, [auth]);

    return null;
}

export default Login;