import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import Layout from './components/Layout';
import ChatPage from './pages/ChatPage';
import MiningPage from './pages/MiningPage';
import KpiPage from './pages/KpiPage';
import RcaPage from './pages/RcaPage';
import DashboardBuilderPage from './pages/DashboardBuilderPage';
import ErrorBoundary from './components/ErrorBoundary';

const queryClient = new QueryClient();

function App() {
  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <Router>
          <Routes>
            <Route path="/" element={<Layout />}>
              <Route index element={<ChatPage />} />
              <Route path="mining" element={<MiningPage />} />
              <Route path="kpi" element={<KpiPage />} />
              <Route path="rca" element={<RcaPage />} />
              <Route path="dashboard" element={<DashboardBuilderPage />} />
            </Route>
          </Routes>
        </Router>
      </QueryClientProvider>
    </ErrorBoundary>
  );
}

export default App;
