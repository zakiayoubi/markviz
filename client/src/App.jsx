import { Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import Register from "./pages/Register";
import Login from "./pages/Login";
import Stock from "./pages/Stock";
import Portfolio from "./pages/Portfolio";
import ProtectedRoute from "./components/ProtectedRoute";

function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/stock/:ticker" element={<Stock />} /> 
      <Route path="/register" element={<Register />} />
      <Route path="/login" element={<Login />} />
      <Route 
      path="/portfolio" 
      element=
      {
      // <ProtectedRoute>
        <Portfolio />
      // </ProtectedRoute>
      } />

    </Routes>
  );
}

export default App;