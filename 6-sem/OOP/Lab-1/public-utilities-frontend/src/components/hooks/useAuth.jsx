import { useContext } from 'react';
import { Navigate } from 'react-router-dom';
import AuthContext from '../context/AuthProvider';

const ROLES = {
    Admin: 'admin',
    Dispatcher: 'dispatcher',
    Tenant: 'tenant',
}

const RequireAuth = ({ children, allowedRoles }) => {
    const auth = useContext(AuthContext);

    if (!auth.isAuthenticated) {
        return <Navigate to="/" />;
    }

    if (allowedRoles && !allowedRoles.some(role => auth.roles.includes(role))) {
        return <Navigate to="/unauthorized" />;
    }

    return children;
};

export default RequireAuth;
