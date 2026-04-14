import Hero from "./pages/Hero";
import Chat from "./pages/Chat";
import Server from "./pages/Server";
import Login from "./pages/Login";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

function RequireAuth({ children }: { children: JSX.Element }) {
  const username = sessionStorage.getItem("username");
  return username ? children : <Navigate to="/login" replace />;
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/" element={<RequireAuth><Hero /></RequireAuth>} />
        <Route path="/chat" element={<RequireAuth><Chat /></RequireAuth>} />
        <Route path="/server" element={<RequireAuth><Server /></RequireAuth>} />
      </Routes>
    </BrowserRouter>
  );
}
