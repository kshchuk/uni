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
import ROLES from "./components/hooks/useAuth";
import Unauthorized from "./components/Unauthorized";

function App() {
    return (
        <AuthProvider>
            <Router>
                <Routes>
                    <Route path='/' element={<Home />}>
                        <Route path='admin' element={<RequireAuth allowedRoles={[ROLES.Admin]} />}>
                            <Route path="view" element={<AdminView />} />
                            <Route path='admin/view_tenants' element={<Tenants />} />
                            <Route path='admin/view_requests' element={<Requests />} />
                            <Route path='admin/view_specialists' element={<Specialists />} />
                            <Route path='admin/view_work_plans' element={<WorkPlans />} />
                            <Route path='admin/view_teams' element={<Teams />} />
                        </Route>

                        <Route path='tenant' element={<RequireAuth allowedRoles={[ROLES.Tenant]} />}>
                            <Route path="tenant/view" element={<TenantView />} />
                            <Route path="tenant/edit_requests" element={<EditRequests />} />
                        </Route>

                        <Route path='dispatcher' element={<RequireAuth allowedRoles={[ROLES.Dispatcher]} />}>
                            <Route path="dispatcher/view" element={<DispatcherView />} />
                            <Route path='dispatcher/view_drequests' element={<ViewRequests />} />
                            <Route path='dispatcher/edit_teams' element={<EditTeams />} />
                            <Route path='dispatcher/edit_workplans' element={<EditWorkPlans />} />
                        </Route>
                        <Route path='/home' element={<Home />} />
                        <Route path='/unauthorized' element={<Unauthorized />} />
                    </Route>
                </Routes>
            </Router>
        </AuthProvider>
    )
}

export default App;
