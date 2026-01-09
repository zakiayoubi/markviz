import { Routes, Route } from "react-router-dom";
import Layout from "./components/layout/Layout"
import Home from "./pages/home/Home";
import Register from "./pages/register/Register";
import Login from "./pages/login/Login";
import Stock from "./pages/stock/Stock"
import Portfolio from "./pages/portfolio/Portfolio";
import Trade from "./pages/trade/Trade";
import ProtectedRoute from "./components/ProtectedRoute";

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/stock/:ticker" element={<Stock />} />
        <Route path="/register" element={<Register />} />
        <Route path="/login" element={<Login />} />
        <Route
          path="/portfolio"
          element={
            <ProtectedRoute>
              <Portfolio />
            </ProtectedRoute>
          }
        />
        <Route
          path="/trade"
          element={
            <ProtectedRoute>
              <Trade />
            </ProtectedRoute>
          }
        />
      </Routes>
    </Layout>
  );
}

export default App;