import React from 'react';
import { X, AlertTriangle } from 'lucide-react';
import { RcaResponse } from '../types';

interface Props {
  data: RcaResponse | null;
  isLoading: boolean;
  onClose: () => void;
  isOpen: boolean;
  inline?: boolean;
}

const RcaPanel: React.FC<Props> = ({ data, isLoading, onClose, isOpen, inline }) => {
  return (
    <div className={inline 
      ? "flex flex-col h-full w-full bg-white rounded-xl shadow-sm border border-slate-100 overflow-hidden" 
      : `fixed inset-y-0 right-0 w-96 bg-white shadow-2xl transform transition-transform duration-300 ease-in-out z-50 ${isOpen ? 'translate-x-0' : 'translate-x-full'}`
    }>
      <div className="flex flex-col h-full">
        <div className="flex items-center justify-between p-4 border-b border-slate-200 bg-slate-50">
          <h2 className="text-lg font-semibold text-slate-800">Root Cause Analysis</h2>
          <button onClick={onClose} className="p-1 rounded-full hover:bg-slate-200 text-slate-500">
            <X size={20} />
          </button>
        </div>
        
        <div className="flex-1 overflow-y-auto p-6 space-y-8">
          {isLoading ? (
            <div className="space-y-4 animate-pulse">
              <div className="h-4 bg-slate-200 rounded w-3/4"></div>
              <div className="h-20 bg-slate-200 rounded"></div>
              <div className="h-4 bg-slate-200 rounded w-1/2 mt-8"></div>
              <div className="h-20 bg-slate-200 rounded"></div>
            </div>
          ) : data ? (
            <>
              {/* Summary */}
              <div className="bg-blue-50 border-l-4 border-blue-500 p-4 rounded-r">
                <h3 className="font-semibold text-blue-900 mb-1 flex items-center"><AlertTriangle size={16} className="mr-2" /> AI Summary</h3>
                <p className="text-sm text-blue-800">{data.rca.summary}</p>
              </div>
              
              {/* Causes */}
              <div>
                <h3 className="text-md font-semibold text-slate-800 mb-3 border-b pb-2">Identified Causes</h3>
                <div className="space-y-4">
                  {data.rca.causes.map((cause, idx) => (
                    <div key={idx} className="bg-white border border-slate-200 rounded-lg p-4 shadow-sm">
                      <div className="flex justify-between items-start mb-2">
                        <h4 className="font-medium text-slate-800">{cause.title}</h4>
                        <span className={`text-xs px-2 py-0.5 rounded font-medium ${
                          cause.severity === 'high' ? 'bg-red-100 text-red-800' :
                          cause.severity === 'medium' ? 'bg-amber-100 text-amber-800' :
                          'bg-emerald-100 text-emerald-800'
                        }`}>
                          {cause.severity}
                        </span>
                      </div>
                      <p className="text-sm text-slate-600 mb-2">{cause.description}</p>
                      <p className="text-xs text-slate-500 mb-2">Affected records: <span className="font-medium">{cause.affected_records}</span></p>
                      <div className="bg-slate-50 p-2 rounded text-sm text-slate-700">
                        <span className="font-semibold">Recommendation: </span>{cause.recommendation}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
              
              {/* Timeline */}
              <div>
                <h3 className="text-md font-semibold text-slate-800 mb-3 border-b pb-2">Event Timeline</h3>
                <div className="relative border-l-2 border-slate-200 ml-3 space-y-6">
                  {data.rca.timeline.map((event, idx) => (
                    <div key={idx} className="relative pl-6">
                      <div className="absolute w-3 h-3 bg-indigo-500 rounded-full -left-[7px] top-1.5 border-2 border-white"></div>
                      <div className="text-xs font-semibold text-indigo-600 mb-1">{event.date}</div>
                      <div className="text-sm font-medium text-slate-800">{event.event}</div>
                      <div className="text-sm text-slate-500">{event.impact}</div>
                    </div>
                  ))}
                </div>
              </div>
            </>
          ) : (
            <div className="text-center text-slate-500 mt-10">Select a KPI to analyze.</div>
          )}
        </div>
      </div>
    </div>
  );
};

export default RcaPanel;
