import { Routes, Route, Navigate } from "react-router-dom";

import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import OperationHub from "./pages/OperationHub";
import Simulation from "./pages/Simulation";
import Scheduler from "./pages/Scheduler";
import ResourceCenter from "./pages/ResourceCenter";
import Deadlock from "./pages/Deadlock";
import ComingSoon from "./pages/ComingSoon";

function App() {

  return (

    <Routes>

      {/* Authentication */}

      <Route
        path="/"
        element={<Login />}
      />

      {/* Dashboard */}

      <Route
        path="/dashboard"
        element={<Dashboard />}
      />

      {/* Features */}

      <Route
        path="/operation"
        element={<OperationHub />}
      />

      <Route
        path="/simulation"
        element={<Simulation />}
      />

      <Route
        path="/scheduler"
        element={<Scheduler />}
      />

      <Route
        path="/resource"
        element={<ResourceCenter />}
      />

      <Route
        path="/deadlock"
        element={<Deadlock />}
      />

      {/* Coming Soon */}

      <Route
        path="/transactions"
        element={<ComingSoon title="Transaction Center" />}
      />

      <Route
        path="/logs"
        element={<ComingSoon title="System Logs" />}
      />

      <Route
        path="/analytics"
        element={<ComingSoon title="Analytics" />}
      />

      {/* Invalid Route */}

      <Route
        path="*"
        element={<Navigate to="/" />}
      />

    </Routes>

  );

}

export default App;