import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
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

function App() {
    return (
        <Router>
            <Routes>
                <Route path='/' element={<Layout />}>
                    {/*<Route path='/' element={<Login />} />*/}
                    {/*<Route element={<RequireAuth allowedRoles={[ROLES.Admin]} />}>*/}
                    {/*    <Route path="admin_view" element={<DispatcherView />} />*/}
                    {/*    <Route path='crew_edit' element={<EditTeam />} />*/}
                    {/*    <Route path='plane_edit' element={<EditPlanes />} />*/}
                    {/*    <Route path='race_edit' element={<EditRaces />} />*/}
                    {/*    <Route path='flight_edit' element={<FlightEdit />} />*/}
                    {/*</Route>*/}
                    {/*<Route element={<RequireAuth allowedRoles={[ROLES.Admin, ROLES.Dispatch, ROLES.User]} />}>*/}
                    {/*    <Route path='brigade_view' element={<Brigades />} />*/}
                    {/*    <Route path='crew_view' element={<Crew />} />*/}
                    {/*    <Route path='flights_view' element={<WorkPlan />} />*/}
                    {/*    <Route path='planes_view' element={<Planes />} />*/}
                    {/*    <Route path='races_view' element={<Races />} />*/}
                    {/*    <Route path='view' element={<View />} />*/}
                    {/*</Route>*/}
                    {/*<Route element={<RequireAuth allowedRoles={[ROLES.Admin, ROLES.Dispatch]} />}>*/}
                    {/*    <Route path="dispatch_view" element={<TenantView />} />*/}
                    {/*    <Route path='brigade_edit' element={<EditBrigades />} />*/}
                    {/*    <Route path='crew_dispatch' element={<CrewDispatch />} />*/}
                    {/*</Route>*/}
                    {/*<Route path='unauthorized' element={<Unauthorized />} />*/}
                    {/*<Route path='home' element={<Home />} />*/}
                    <Route path='/view_tenants' element={<Tenants />} />
                    <Route path='/view_requests' element={<Requests />} />
                    <Route path='/view_specialists' element={<Specialists />} />
                    <Route path='/view_work_plans' element={<WorkPlans />} />
                    <Route path='/view_teams' element={<Teams />} />
                    <Route path="/admin_view" element={<DispatcherView />} />
                    <Route path="/tenant_view" element={<TenantView />} />
                    <Route path="/edit_requests" element={<EditRequests />} />
                    <Route path='/view' element={<View />} />
                    <Route path='/home' element={<Home />} />
                </Route>
            </Routes>
        </Router>
    )
}

export default App;
