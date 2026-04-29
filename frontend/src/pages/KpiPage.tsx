import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { kpiApi } from '../api/kpiApi';
import KpiTile from '../components/KpiTile';
import RcaPanel from '../components/RcaPanel';
import { useAppStore } from '../store/appStore';

const KpiPage: React.FC = () => {
  const [filter, setFilter] = useState<string>('All');
  const { selectedKpi, setSelectedKpi } = useAppStore();
  
  const { data: kpis, isLoading, isError, error, refetch } = useQuery({
    queryKey: ['kpis'],
    queryFn: kpiApi.getAll,
    refetchInterval: 30000,
  });

  const { data: rcaData, isLoading: isRcaLoading } = useQuery({
    queryKey: ['rca', selectedKpi],
    queryFn: () => selectedKpi ? kpiApi.getRca(selectedKpi) : null,
    enabled: !!selectedKpi,
  });

  const modules = ['All', 'FI', 'SD', 'MM', 'PP'];

  const filteredKpis = kpis ? (filter === 'All' ? kpis : kpis.filter(k => k.module === filter)) : [];

  return (
    <div className="relative h-full flex flex-col bg-slate-50">
      <div className="p-6 pb-2 border-b border-slate-200 bg-white shadow-sm z-10 flex-shrink-0">
        <h1 className="text-2xl font-bold text-slate-800 mb-4">KPI Dashboard</h1>
        <div className="flex space-x-2">
          {modules.map(m => (
            <button
              key={m}
              onClick={() => setFilter(m)}
              className={`px-4 py-1.5 rounded-full text-sm font-medium transition-colors ${
                filter === m ? 'bg-indigo-600 text-white' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              }`}
            >
              {m === 'All' ? 'All Modules' : m}
            </button>
          ))}
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-6">
        {isLoading ? (
          <div className="flex justify-center mt-10">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
          </div>
        ) : isError ? (
          <div className="flex flex-col items-center justify-center mt-16 space-y-3">
            <p className="text-red-500 font-medium text-lg">Failed to load KPI data</p>
            <p className="text-slate-400 text-sm">
              {(error as Error)?.message || 'Could not connect to the backend API'}
            </p>
            <button
              onClick={() => refetch()}
              className="mt-2 px-5 py-2 bg-indigo-600 text-white rounded-lg text-sm hover:bg-indigo-700 transition-colors"
            >
              Retry
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 max-w-7xl mx-auto">
            {filteredKpis.map(kpi => (
              <KpiTile key={kpi.id} kpi={kpi} onClick={setSelectedKpi} />
            ))}
          </div>
        )}
      </div>

      {selectedKpi && (
        <div className="fixed inset-y-0 right-0 w-[520px] bg-white shadow-2xl z-50 flex flex-col border-l border-slate-200 overflow-hidden transform transition-transform duration-300 translate-x-0">
          <RcaPanel 
            isOpen={!!selectedKpi} 
            onClose={() => setSelectedKpi(null)} 
            data={rcaData as any} 
            isLoading={isRcaLoading} 
            inline={false}
          />
        </div>
      )}
    </div>
  );
};

export default KpiPage;
