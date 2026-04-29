import React from 'react';

interface Props {
  status: 'green' | 'amber' | 'red';
}

const StatusBadge: React.FC<Props> = ({ status }) => {
  const isGreen = status === 'green';
  const isAmber = status === 'amber';
  const text = isGreen ? 'On Track' : isAmber ? 'Monitor' : 'Critical';
  const color = isGreen ? 'bg-emerald-100 text-emerald-800' : isAmber ? 'bg-amber-100 text-amber-800' : 'bg-red-100 text-red-800';

  return (
    <span className={`text-xs font-semibold px-2.5 py-0.5 rounded ${color}`}>
      {text}
    </span>
  );
};

export default StatusBadge;
