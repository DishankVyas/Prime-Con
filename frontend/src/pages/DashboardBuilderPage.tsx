import React, { useState } from 'react';
import { LayoutDashboard, Send } from 'lucide-react';
import { apiClient } from '../api/client';
import ChartRenderer from '../components/ChartRenderer';
import ErrorBoundary from '../components/ErrorBoundary';

const DashboardBuilderPage: React.FC = () => {
  const [prompt, setPrompt] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [panels, setPanels] = useState<any[]>([]);
  const [error, setError] = useState<string | null>(null);

  const handleGenerate = async () => {
    if (!prompt.trim() || isLoading) return;
    setIsLoading(true);
    setError(null);
    setPanels([]);

    try {
      const { data } = await apiClient.post('/api/dashboard/generate', { prompt });
      setPanels(data.panels || []);
    } catch (e: any) {
      setError(e.response?.data?.detail || e.message || 'Failed to generate dashboard');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full bg-slate-50 relative p-6">
      <div className="mb-6 flex flex-col space-y-4 max-w-4xl mx-auto w-full">
        <div className="flex items-center space-x-2 text-slate-800">
          <LayoutDashboard size={28} />
          <h1 className="text-2xl font-bold">NL Dashboard Builder</h1>
        </div>
        <div className="relative flex items-center shadow-sm">
          <input
            type="text"
            className="w-full bg-white border border-slate-300 rounded-xl pl-4 pr-12 py-3 focus:outline-none focus:ring-2 focus:ring-indigo-500"
            placeholder="E.g., Build me a dashboard for Order to Cash KPIs..."
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') handleGenerate();
            }}
          />
          <button
            onClick={handleGenerate}
            disabled={!prompt.trim() || isLoading}
            className="absolute right-2 text-indigo-600 hover:text-indigo-800 disabled:opacity-50"
          >
            <Send size={20} />
          </button>
        </div>
        {error && <div className="text-red-500 text-sm mt-2">{error}</div>}
      </div>

      <div className="flex-1 overflow-y-auto max-w-6xl mx-auto w-full">
        {isLoading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {[1, 2, 3, 4].map(i => (
              <div key={i} className="bg-white border border-slate-200 rounded-xl p-4 h-[350px] flex flex-col animate-pulse">
                <div className="h-4 bg-slate-200 rounded w-1/3 mb-4"></div>
                <div className="flex-1 bg-slate-100 rounded"></div>
              </div>
            ))}
          </div>
        ) : panels.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {panels.map((panel, idx) => (
              <div key={idx} className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm flex flex-col h-[350px]">
                <h3 className="text-sm font-bold text-slate-800 mb-4">{panel.title}</h3>
                {panel.error ? (
                  <div className="text-sm text-red-500">{panel.error}</div>
                ) : panel.data && panel.data.length > 0 ? (
                  <div className="flex-1 w-full min-h-0">
                    <ErrorBoundary>
                      <ChartRenderer chartConfig={panel.chart_config} data={panel.data} />
                    </ErrorBoundary>
                  </div>
                ) : (
                  <div className="text-sm text-slate-500 italic">No data returned</div>
                )}
              </div>
            ))}
          </div>
        ) : (
          <div className="h-full flex items-center justify-center text-slate-400">
            Type a prompt above to generate a custom dashboard.
          </div>
        )}
      </div>
    </div>
  );
};

export default DashboardBuilderPage;
