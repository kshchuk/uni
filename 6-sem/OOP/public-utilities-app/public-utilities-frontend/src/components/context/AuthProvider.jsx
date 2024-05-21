import { createContext, useState, useEffect } from "react";
import kc from '../hooks/Auth';

const AuthContext = createContext({});

export const AuthProvider = ({children}) => {
    const [auth, setAuth] = useState({});

    useEffect(() => {
        console.log(kc.authenticated)
        if (kc.authenticated) {
            setAuth({
                isAuthenticated: kc.authenticated,
                token: kc.token,
                roles: kc.realmAccess.roles,
                login: kc.login,
                logout: kc.logout,
                updateToken: kc.updateToken,
                hasRealmRole: kc.hasRealmRole,
                hasResourceRole: kc.hasResourceRole,
            });
        }
    }, [kc.authenticated]);

    return (
        <AuthContext.Provider value={auth}>
            {children}
        </AuthContext.Provider>
    )
}

export default AuthContext;
