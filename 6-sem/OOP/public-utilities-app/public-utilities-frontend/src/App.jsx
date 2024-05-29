import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { AuthProvider } from './components/context/AuthProvider';
import RequireAuth from "./components/RequireAuth";
import Home from "./components/Home";
import TenantView from "./components/admin_pages/TenantView";
import DispatcherView from "./components/admin_pages/DispatcherView";
import Tenants from "./components/pages/Tenants";
import Requests from "./components/pages/Requests";
import Specialists from "./components/pages/Specialists";
import WorkPlans from "./components/pages/WorkPlans";
import Teams from "./components/pages/Teams";
import EditRequests from "./components/admin_pages/EditRequests";
import EditTeams from "./components/admin_pages/EditTeams";
import EditWorkPlans from "./components/admin_pages/EditWorkPlans";
import ViewRequests from "./components/admin_pages/ViewRequests";
import AdminView from "./components/admin_pages/AdminView";
import Unauthorized from "./components/Unauthorized";
import { Navigate } from "react-router-dom";

const ROLES = {
    Admin: 'admin',
    Dispatcher: 'dispatcher',
    Tenant: 'tenant',
};

function App() {
    return (
        <AuthProvider>
            <Router>
                <Routes>
                    <Route path="/" element={<Home />} />
                    <Route path="/home" element={<Home />} />
                    <Route path="/unauthorized" element={<Unauthorized />} />

                    <Route element={<RequireAuth allowedRoles={[ROLES.Admin]} />}>
                        <Route path="/admin_view" element={<AdminView />}>
                            <Route path="view_tenants" element={<Tenants />} />
                            <Route path="view_requests" element={<Requests />} />
                            <Route path="view_specialists" element={<Specialists />} />
                            <Route path="view_work_plans" element={<WorkPlans />} />
                            <Route path="view_teams" element={<Teams />} />
                        </Route>
                    </Route>

                    <Route element={<RequireAuth allowedRoles={[ROLES.Admin, ROLES.Tenant]} />}>
                        <Route path="/tenant_view" element={<TenantView />}>
                            <Route path="edit_requests" element={<EditRequests />} />
                        </Route>
                    </Route>

                    <Route element={<RequireAuth allowedRoles={[ROLES.Admin, ROLES.Dispatcher]} />}>
                        <Route path="/dispatcher_view" element={<DispatcherView />}>
                            <Route path="view_drequests" element={<ViewRequests />} />
                            <Route path="edit_teams" element={<EditTeams />} />
                            <Route path="edit_workplans" element={<EditWorkPlans />} />
                        </Route>
                    </Route>
                </Routes>
            </Router>
        </AuthProvider>
    )
}

export default App;
