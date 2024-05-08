import { useContext } from 'react';
import { Navigate } from 'react-router-dom';
import AuthContext from './context/AuthProvider';
import { Outlet } from 'react-router-dom';

const RequireAuth = ({ allowedRoles }) => {
    const auth = useContext(AuthContext);

    if (!auth.isAuthenticated) {
        return <Navigate to="/" />;
    }

    if (allowedRoles && !allowedRoles.some(role => auth.roles.includes(role))) {
        return <Navigate to="/unauthorized" />;
    }

    return <Outlet />;
};

export default RequireAuth;
