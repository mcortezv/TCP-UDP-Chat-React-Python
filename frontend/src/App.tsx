import Hero from "./pages/Hero";
import Config from "./pages/Server";
import { BrowserRouter, Routes, Route } from "react-router-dom";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Hero />} />
        <Route path="/server" element={<Config />} />
      </Routes>
    </BrowserRouter>
  );
}
