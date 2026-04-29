import React from 'react';
import RcaPanel from '../components/RcaPanel';
import { useAppStore } from '../store/appStore';
import { useQuery } from '@tanstack/react-query';
import { kpiApi } from '../api/kpiApi';

const RcaPage: React.FC = () => {
  const { selectedKpi, setSelectedKpi } = useAppStore();
  
  const { data: kpis } = useQuery({
    queryKey: ['kpis'],
    queryFn: kpiApi.getAll,
  });

  const { data: rcaData, isLoading: isRcaLoading } = useQuery({
    queryKey: ['rca', selectedKpi],
    queryFn: () => selectedKpi ? kpiApi.getRca(selectedKpi) : null,
    enabled: !!selectedKpi,
  });

  return (
    <div className="flex h-full bg-slate-50">
      <div className="w-1/3 max-w-sm bg-white border-r border-slate-200 flex flex-col h-full">
        <div className="p-6 border-b border-slate-200">
          <h2 className="text-xl font-bold text-slate-800">Select KPI</h2>
          <p className="text-sm text-slate-500 mt-1">Analyze underlying root causes</p>
        </div>
        <div className="flex-1 overflow-y-auto p-4 space-y-2">
          {kpis?.map(kpi => (
            <button
              key={kpi.id}
              onClick={() => setSelectedKpi(kpi.id)}
              className={`w-full text-left p-3 rounded-lg border transition-all flex items-center justify-between ${
                selectedKpi === kpi.id ? 'bg-indigo-50 border-indigo-200 ring-1 ring-indigo-500' : 'bg-white border-slate-200 hover:bg-slate-50'
              }`}
            >
              <div>
                <div className="font-semibold text-slate-800 text-sm">{kpi.name}</div>
                <div className="text-xs text-slate-500">{kpi.module}</div>
              </div>
              <div className={`w-3 h-3 rounded-full ${kpi.status === 'green' ? 'bg-emerald-500' : kpi.status === 'amber' ? 'bg-amber-500' : 'bg-red-500'}`}></div>
            </button>
          ))}
        </div>
      </div>
      
      <div className="flex-1 overflow-hidden relative">
        {selectedKpi ? (
          <RcaPanel 
            isOpen={true} 
            onClose={() => setSelectedKpi(null)} 
            data={rcaData as any} 
            isLoading={isRcaLoading} 
            inline={true}
          />
        ) : (
          <div className="flex h-full items-center justify-center text-slate-400">
            Select a KPI from the left to view Root Cause Analysis
          </div>
        )}
      </div>
    </div>
  );
};

export default RcaPage;
