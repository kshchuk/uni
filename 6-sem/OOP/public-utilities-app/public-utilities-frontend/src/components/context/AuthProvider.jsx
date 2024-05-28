import { createContext, useState, useEffect } from 'react';
import { kc } from '../hooks/Auth';

const AuthContext = createContext({});

export const AuthProvider = ({ children }) => {
    const [auth, setAuth] = useState({
        isAuthenticated: false,
        token: null,
        roles: [],
        login: () => {},
        logout: () => {},
        updateToken: () => {},
        hasRealmRole: () => false,
        hasResourceRole: () => false,
    });

    useEffect(() => {
        const initAuth = async () => {
            try {
                if (kc.authenticated) {
                    setAuth({
                        isAuthenticated: kc.authenticated,
                        token: kc.token,
                        roles: kc.realmAccess.roles || [],
                        login: kc.login,
                        logout: kc.logout,
                        updateToken: kc.updateToken,
                        hasRealmRole: kc.hasRealmRole,
                        hasResourceRole: kc.hasResourceRole,
                    });
                }
            } catch (error) {
                console.error("Failed to initialize Keycloak:", error);
            }
        };

        initAuth();
    }, []);

    return (
        <AuthContext.Provider value={auth}>
            {children}
        </AuthContext.Provider>
    );
};

export default AuthContext;
