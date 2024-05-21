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
import Layout from "./components/Layout";
import View from "./components/pages/View";
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
                    <Route path='/' element={<Layout />}>
                        <Route path='admin' element={<RequireAuth allowedRoles={[ROLES.Admin]} />}>
                            <Route path="/view" element={<AdminView />} />
                            <Route path='/view_tenants' element={<Tenants />} />
                            <Route path='/view_requests' element={<Requests />} />
                            <Route path='/view_specialists' element={<Specialists />} />
                            <Route path='/view_work_plans' element={<WorkPlans />} />
                            <Route path='/view_teams' element={<Teams />} />
                        </Route>

                        <Route path='tenant' element={<RequireAuth allowedRoles={[ROLES.Tenant]} />}>
                            <Route path="/view" element={<TenantView />} />
                            <Route path="/edit_requests" element={<EditRequests />} />
                        </Route>

                        <Route path='dispatcher' element={<RequireAuth allowedRoles={[ROLES.Dispatcher]} />}>
                            <Route path="/view" element={<DispatcherView />} />
                            <Route path='/view_drequests' element={<ViewRequests />} />
                            <Route path='/edit_teams' element={<EditTeams />} />
                            <Route path='/edit_workplans' element={<EditWorkPlans />} />
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
