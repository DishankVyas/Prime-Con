import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { kpiApi } from '../api/kpiApi';
import { AlertCircle, X, ArrowRight } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useAppStore } from '../store/appStore';

interface AlertDrawerProps {
  isOpen: boolean;
  onClose: () => void;
}

const AlertDrawer: React.FC<AlertDrawerProps> = ({ isOpen, onClose }) => {
  const navigate = useNavigate();
  const { setSelectedKpi } = useAppStore();

  const { data: kpis } = useQuery({
    queryKey: ['kpis'],
    queryFn: kpiApi.getAll,
    refetchInterval: 30000,
  });

  const criticalKpis = kpis?.filter((k: any) => k.status === 'red') || [];

  const handleAnalyze = (id: string) => {
    setSelectedKpi(id);
    navigate('/kpi');
    onClose();
  };

  return (
    <>
      {isOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-20 z-40 transition-opacity" onClick={onClose} />
      )}
      <div
        className={`fixed inset-y-0 right-0 w-96 bg-white shadow-2xl z-50 transform transition-transform duration-300 ease-in-out flex flex-col ${
          isOpen ? 'translate-x-0' : 'translate-x-full'
        }`}
      >
        <div className="p-4 border-b border-slate-200 flex items-center justify-between bg-slate-50">
          <div className="flex items-center text-red-600 font-semibold">
            <AlertCircle size={20} className="mr-2" />
            Critical Alerts ({criticalKpis.length})
          </div>
          <button onClick={onClose} className="p-1 hover:bg-slate-200 rounded text-slate-500">
            <X size={20} />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {criticalKpis.length === 0 ? (
            <div className="text-sm text-slate-500 text-center mt-10">No critical alerts.</div>
          ) : (
            criticalKpis.map((kpi: any) => (
              <div key={kpi.id} className="border border-red-200 bg-red-50 rounded-xl p-4 shadow-sm">
                <div className="flex justify-between items-start mb-2">
                  <h4 className="font-bold text-slate-800">{kpi.name}</h4>
                  <span className="text-xs font-semibold px-2 py-1 bg-red-100 text-red-700 rounded-full">
                    {kpi.module}
                  </span>
                </div>
                <div className="text-sm text-slate-600 mb-3">
                  Current: <span className="font-bold text-red-600">{kpi.value} {kpi.unit}</span>
                  <br/>
                  Threshold: <span className="text-slate-500">{kpi.threshold_red} {kpi.unit}</span>
                </div>
                <button
                  onClick={() => handleAnalyze(kpi.id)}
                  className="w-full flex items-center justify-center py-2 bg-white border border-red-200 rounded-lg text-sm font-medium text-red-700 hover:bg-red-50 transition-colors"
                >
                  Analyze Root Cause <ArrowRight size={16} className="ml-1" />
                </button>
              </div>
            ))
          )}
        </div>
      </div>
    </>
  );
};

export default AlertDrawer;
