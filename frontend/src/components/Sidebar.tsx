import React, { useEffect, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { MessageSquare, LayoutDashboard, Activity, AlertCircle, LayoutPanelLeft, Bell } from 'lucide-react';
import { apiClient } from '../api/client';
import { useQuery } from '@tanstack/react-query';
import { kpiApi } from '../api/kpiApi';
import AlertDrawer from './AlertDrawer';

const Sidebar: React.FC = () => {
  const location = useLocation();
  const [isHealthy, setIsHealthy] = useState(false);
  const [isAlertsOpen, setIsAlertsOpen] = useState(false);

  useEffect(() => {
    const checkHealth = async () => {
      try {
        await apiClient.get('/health');
        setIsHealthy(true);
      } catch (error) {
        setIsHealthy(false);
      }
    };
    
    checkHealth();
    const interval = setInterval(checkHealth, 10000);
    return () => clearInterval(interval);
  }, []);

  const { data: kpis } = useQuery({
    queryKey: ['kpis'],
    queryFn: kpiApi.getAll,
    refetchInterval: 30000,
  });
  
  const criticalCount = kpis?.filter((k: any) => k.status === 'red').length || 0;

  const links = [
    { path: '/', label: 'Chat', icon: <MessageSquare size={20} /> },
    { path: '/dashboard', label: 'NL Dashboard', icon: <LayoutPanelLeft size={20} /> },
    { path: '/mining', label: 'Process Mining', icon: <Activity size={20} /> },
    { path: '/kpi', label: 'KPI Dashboard', icon: <LayoutDashboard size={20} /> },
    { path: '/rca', label: 'Root Cause Analysis', icon: <AlertCircle size={20} /> },
  ];

  return (
    <div className="w-64 bg-white border-r border-slate-200 flex flex-col h-full">
      <div className="p-6">
        <h1 className="text-slate-900 text-xl font-bold">PrimeConSemLayer</h1>
        <p className="text-slate-500 text-sm mt-1">SAP AI Analytics</p>
      </div>
      <nav className="flex-1 px-4 space-y-2">
          {links.map((link) => (
            <Link
              key={link.path}
              to={link.path}
              className={`flex items-center px-4 py-3 rounded-xl transition-all ${
                location.pathname === link.path
                  ? 'bg-indigo-50 text-indigo-700 font-semibold'
                  : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
              }`}
            >
              <div className="mr-3">{link.icon}</div>
              <span className="text-sm">{link.label}</span>
            </Link>
          ))}
          
          <button
            onClick={() => setIsAlertsOpen(true)}
            className="w-full flex items-center px-4 py-3 rounded-xl transition-all text-slate-600 hover:bg-slate-50 hover:text-slate-900 relative"
          >
            <div className="mr-3 relative">
              <Bell size={20} />
              {criticalCount > 0 && (
                <span className="absolute -top-1 -right-1 flex h-3 w-3">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-3 w-3 bg-red-500"></span>
                </span>
              )}
            </div>
            <span className="text-sm">Alerts</span>
            {criticalCount > 0 && (
              <span className="ml-auto bg-red-100 text-red-600 text-xs font-bold px-2 py-0.5 rounded-full">
                {criticalCount}
              </span>
            )}
          </button>
        </nav>
      
      <div className="p-6 border-t border-slate-200">
        <div className="flex items-center">
          <div className={`w-2.5 h-2.5 rounded-full mr-2 ${isHealthy ? 'bg-emerald-500' : 'bg-red-500'}`}></div>
          <span className="text-xs font-medium text-slate-500">
            {isHealthy ? 'System Online' : 'System Offline'}
          </span>
        </div>
      </div>
      
      <AlertDrawer isOpen={isAlertsOpen} onClose={() => setIsAlertsOpen(false)} />
    </div>
  );
};

export default Sidebar;
