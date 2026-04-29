import React from 'react';
import { ResponsiveContainer, LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, CartesianGrid, XAxis, YAxis, Tooltip, Legend, ComposedChart } from 'recharts';

interface ChartRendererProps {
  chartConfig?: { type: string; data?: any[]; config?: any };
  config?: any;
  data?: any[];
}

const COLORS = ['#6366f1', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4', '#f43f5e', '#14b8a6'];

const ChartRenderer: React.FC<ChartRendererProps> = ({ chartConfig, config: configProp, data: dataProp }) => {
  const config = chartConfig || configProp;
  const data = chartConfig?.data || dataProp;

  if (!config || !data || data.length === 0) return null;

  if (config.type === 'LineChart') {
    return (
      <ResponsiveContainer width="100%" height={config.config?.height || 280}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" vertical={false} />
          <XAxis dataKey={config.config.xKey} />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey={config.config.yKey} stroke={config.config.color || "#6366f1"} strokeWidth={2} />
        </LineChart>
      </ResponsiveContainer>
    );
  }

  if (config.type === 'BarChart') {
    return (
      <ResponsiveContainer width="100%" height={config.config?.height || 280}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" vertical={false} />
          <XAxis dataKey={config.config.xKey} />
          <YAxis />
          <Tooltip />
          <Legend />
          <Bar dataKey={config.config.yKey} fill={config.config.color || "#10b981"} />
        </BarChart>
      </ResponsiveContainer>
    );
  }

  if (config.type === 'PieChart') {
    return (
      <ResponsiveContainer width="100%" height={config.config?.height || 280}>
        <PieChart>
          <Pie data={data} dataKey={config.config.valueKey} nameKey={config.config.nameKey} cx="50%" cy="50%" outerRadius={100} label>
            {data.map((_, index) => <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />)}
          </Pie>
          <Tooltip />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
    );
  }

  if (config.type === 'ComposedChart') {
    const yKeys: string[] = config.config?.yKeys || [];
    const xKey: string = config.config?.xKey;
    return (
      <ResponsiveContainer width="100%" height={config.config?.height || 280}>
        <ComposedChart data={data}>
          <CartesianGrid strokeDasharray="3 3" vertical={false} />
          <XAxis dataKey={xKey} />
          <YAxis />
          <Tooltip />
          <Legend />
          {yKeys.map((k, i) => (
            <Line
              key={k}
              type="monotone"
              dataKey={k}
              stroke={COLORS[i % COLORS.length]}
              strokeWidth={2}
              dot={false}
            />
          ))}
        </ComposedChart>
      </ResponsiveContainer>
    );
  }

  if (config.type === 'DataTable') {
    const columns = Object.keys(data[0] || {});
    return (
      <div className="overflow-auto max-h-[280px]">
        <table className="min-w-full text-sm text-left">
          <thead className="text-xs text-slate-700 uppercase bg-slate-50 sticky top-0">
            <tr>
              {columns.map(col => <th key={col} className="px-6 py-3">{col}</th>)}
            </tr>
          </thead>
          <tbody>
            {data.map((row, i) => (
              <tr key={i} className="bg-white border-b hover:bg-slate-50">
                {columns.map(col => <td key={col} className="px-6 py-4">{row[col]}</td>)}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  }

  if (config.type === 'KpiGrid') {
    return (
      <div className="grid grid-cols-2 gap-4 mt-2">
        {data.map((item: any, i: number) => (
          <div key={i} className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex flex-col items-center justify-center text-center h-28">
            <div className="text-sm text-slate-500 font-medium mb-1">{item.kpi}</div>
            <div className="text-2xl font-bold text-slate-900">
              {item.value} <span className="text-sm font-normal text-slate-500 ml-1">{item.unit}</span>
            </div>
          </div>
        ))}
      </div>
    );
  }

  return <div>Unsupported chart type: {config.type}</div>;
};

export default ChartRenderer;
