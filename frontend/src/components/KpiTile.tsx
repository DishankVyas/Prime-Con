import React from 'react';
import { KpiData } from '../types';
import SparkLine from './SparkLine';
import StatusBadge from './StatusBadge';

interface Props {
  kpi: KpiData;
  onClick: (id: string) => void;
}

const KpiTile: React.FC<Props> = ({ kpi, onClick }) => {
  const isGreen = kpi.status === 'green';
  const isAmber = kpi.status === 'amber';
  const borderColor = isGreen ? 'border-emerald-500' : (isAmber ? 'border-amber-500' : 'border-red-500');

  const formatValue = (value: number, unit: string) => {
    if (unit === 'EUR') return value.toLocaleString('en-EU', { maximumFractionDigits: 0 });
    if (unit === '%') return value.toFixed(1);
    if (unit === 'ratio') return value.toFixed(1);
    if (unit === 'days' || unit === 'count') return value.toFixed(unit === 'count' ? 0 : 1);
    return value.toLocaleString();
  };

  return (
    <div 
      className={`bg-white rounded-lg shadow-sm border border-slate-200 border-l-4 ${borderColor} p-5 cursor-pointer hover:shadow-md transition-shadow`}
      onClick={() => onClick(kpi.id)}
    >
      <div className="flex justify-between items-start mb-2">
        <h3 className="text-sm font-medium text-slate-600 line-clamp-1" title={kpi.name}>{kpi.name}</h3>
        <span className="bg-slate-100 text-slate-600 text-xs px-2 py-1 rounded font-medium">{kpi.module}</span>
      </div>
      <div className="flex items-baseline space-x-1 mb-4">
        <span className="text-3xl font-bold text-slate-900">{formatValue(kpi.value, kpi.unit)}</span>
        <span className="text-sm text-slate-500">{kpi.unit}</span>
      </div>
      
      <div className="mb-4">
        <SparkLine data={kpi.trend} status={kpi.status} />
      </div>
      
      <div className="mt-auto">
        <StatusBadge status={kpi.status} />
      </div>
    </div>
  );
};

export default KpiTile;
