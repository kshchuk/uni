import { useLocation, Navigate, Outlet } from "react-router-dom";
import useAuth from "./hooks/useAuth";
import { jwtDecode } from "jwt-decode";

const RequireAuth = ({ allowedRoles }) =>{
    const auth = jwtDecode(window.localStorage.getItem("Token"));
    const location = useLocation();
    console.log(allowedRoles)
    console.log(auth.role)
    return(
        allowedRoles?.includes(auth?.role)
        ? <Outlet/>
        : <Navigate to="unauthorized" state={{from: location}} replace/>
    );
}

export default RequireAuth;