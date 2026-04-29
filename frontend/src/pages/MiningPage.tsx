import React, { useState } from 'react';
import ProcessGraph from '../components/ProcessGraph';
import { Activity } from 'lucide-react';
import { apiClient } from '../api/client';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';

const MiningPage: React.FC = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [data, setData] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<'dfg' | 'petri'>('dfg');
  const sources = [
    { id: 'O2C', name: 'Order to Cash', description: 'From Sales Order to Payment' },
    { id: 'P2P', name: 'Procure to Pay', description: 'From Purchase Order to Invoice' },
  ];

  const handleDiscover = async (sourceId: string) => {
    setIsLoading(true);
    setError(null);
    try {
      const endpoint = viewMode === 'petri' ? '/api/mining/petri' : '/api/mining/discover';
      const res = await apiClient.post(endpoint, { source: sourceId });
      setData(res.data);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Process discovery failed. Please check your data and try again.';
      setError(message);
      setIsLoading(false);
      return;
    }
    setIsLoading(false);
  };

  const activityData = data?.graph?.nodes
    ?.sort((a: any, b: any) => b.frequency - a.frequency)
    ?.slice(0, 8)
    ?.map((n: any) => ({ name: n.label, frequency: n.frequency })) || [];

  return (
    <div className="flex h-full bg-slate-50 overflow-hidden">
      {/* Sidebar Controls */}
      <div className="w-72 bg-white border-r border-slate-200 p-6 flex flex-col space-y-6">
        <div>
          <h2 className="text-lg font-bold text-slate-800 flex items-center mb-1">
            <Activity className="mr-2" size={20} /> Process Mining
          </h2>
          <p className="text-sm text-slate-500">Discover and analyze business processes.</p>
        </div>

        <div className="space-y-4">
          <div className="space-y-2">
            <h3 className="text-sm font-semibold text-slate-700 uppercase tracking-wider">View Mode</h3>
            <div className="flex rounded-lg overflow-hidden border border-slate-200">
              <button
                onClick={() => setViewMode('dfg')}
                className={`flex-1 py-2 text-sm font-medium transition-colors ${viewMode === 'dfg' ? 'bg-indigo-600 text-white' : 'bg-white text-slate-600 hover:bg-slate-50'}`}
              >
                DFG
              </button>
              <button
                onClick={() => setViewMode('petri')}
                className={`flex-1 py-2 text-sm font-medium transition-colors ${viewMode === 'petri' ? 'bg-indigo-600 text-white' : 'bg-white text-slate-600 hover:bg-slate-50'}`}
              >
                Petri Net
              </button>
            </div>
          </div>

          <h3 className="text-sm font-semibold text-slate-700 uppercase tracking-wider mt-4">Select Source</h3>
          
          {sources.map((selectedSource) => (
            <button 
              key={selectedSource.id}
              onClick={() => handleDiscover(selectedSource.id)}
              className="w-full text-left p-4 border border-slate-200 rounded-xl hover:border-indigo-500 hover:shadow-md transition-all focus:ring-2 focus:ring-indigo-500"
            >
              <div className="font-bold text-slate-800">{selectedSource.name}</div>
              <div className="text-xs text-slate-500 mt-1">{selectedSource.description}</div>
            </button>
          ))}

          {error && (
            <div className="p-3 bg-red-50 text-red-700 text-sm rounded-lg border border-red-200">
              {error}
            </div>
          )}
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 p-6 overflow-y-auto">
        {isLoading ? (
          <div className="h-full flex items-center justify-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
          </div>
        ) : data ? (
          <div className="space-y-6 max-w-6xl mx-auto">
            {/* Stats row */}
            <div className="grid grid-cols-4 gap-4">
              <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
                <div className="text-sm text-slate-500 font-medium mb-1">Cases Analyzed</div>
                <div className="text-2xl font-bold text-slate-900">{data.case_count.toLocaleString()}</div>
              </div>
              <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
                <div className="text-sm text-slate-500 font-medium mb-1">Avg Duration</div>
                <div className="text-2xl font-bold text-slate-900">{data.performance.avg_duration_hours.toFixed(1)} hrs</div>
              </div>
              <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
                <div className="text-sm text-slate-500 font-medium mb-1">Fitness</div>
                <div className="text-2xl font-bold text-emerald-600">{(data.conformance.fitness * 100).toFixed(1)}%</div>
              </div>
              <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
                <div className="text-sm text-slate-500 font-medium mb-1">Bottleneck</div>
                <div className="text-lg font-bold text-red-600 truncate" title={data.performance.bottleneck_activity}>
                  {data.performance.bottleneck_activity}
                </div>
              </div>
            </div>

            {/* Graph */}
            <ProcessGraph data={data.type === 'petri_net' ? data : data.graph} />

            {/* Activity Frequency Chart */}
            {activityData.length > 0 && (
              <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-4">
                <h3 className="text-sm font-semibold text-slate-700 mb-3">Activity Frequency</h3>
                <ResponsiveContainer width="100%" height={200}>
                  <BarChart data={activityData} layout="vertical" margin={{ left: 80 }}>
                    <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                    <XAxis type="number" tick={{ fontSize: 11 }} />
                    <YAxis type="category" dataKey="name" tick={{ fontSize: 11 }} width={80} />
                    <Tooltip />
                    <Bar dataKey="frequency" fill="#6366f1" radius={[0, 4, 4, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}
          </div>
        ) : (
          <div className="h-full flex items-center justify-center text-slate-400">
            Select a process source from the left panel to begin analysis.
          </div>
        )}
      </div>
    </div>
  );
};

export default MiningPage;
