import Hero from "./pages/Hero";
import Chat from "./pages/Chat";
import Config from "./pages/Server";
import { BrowserRouter, Routes, Route } from "react-router-dom";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Hero />} />
        <Route path="/chat" element={<Chat />} />
        <Route path="/server" element={<Config />} />
      </Routes>
    </BrowserRouter>
  );
}
