import React from 'react';

interface SparkLineProps {
  data: number[];
  color?: string;
  status?: 'green' | 'amber' | 'red';
}

const SparkLine: React.FC<SparkLineProps> = ({ data, color, status }) => {
  if (!data || data.length < 2) return null;
  const strokeColor = color ?? (status === 'red' ? '#ef4444' : status === 'amber' ? '#f59e0b' : '#10b981');

  const w = 120;
  const h = 32;
  const padding = 3;

  const max = Math.max(...data);
  const min = Math.min(...data);
  const range = max - min || 1; // prevent division by zero

  const points = data.map((v, i) => {
    const x = (i / (data.length - 1)) * w;
    const y = padding + ((max - v) / range) * (h - padding * 2);
    return `${x.toFixed(1)},${y.toFixed(1)}`;
  }).join(' ');

  return (
    <svg
      viewBox={`0 0 ${w} ${h}`}
      className="w-full h-8"
      preserveAspectRatio="none"
    >
      <polyline
        points={points}
        fill="none"
        stroke={strokeColor}
        strokeWidth="1.8"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
};

export default SparkLine;
