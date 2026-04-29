import React from 'react';
import { ChatMessage as ChatMessageType } from '../types';
import ErrorBoundary from './ErrorBoundary';
import ChartRenderer from './ChartRenderer';
import { exportToCSV } from '../utils/export';
import { Download } from 'lucide-react';

interface Props {
  message: ChatMessageType;
}

const ChatMessage: React.FC<Props> = ({ message }) => {
  const isUser = message.role === 'user';
  const errorMessage = (message as any).error as string | undefined;

  return (
    <div className={`flex w-full mb-6 ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div
        className={`max-w-3xl rounded-2xl px-6 py-4 ${
          isUser ? 'bg-indigo-600 text-white' : 'bg-white border border-slate-200 text-slate-800 shadow-sm'
        }`}
      >
        {isUser ? (
          <p>{message.content}</p>
        ) : (
          <div className="space-y-4 w-full">
            {errorMessage && (
              <div className="border border-red-300 bg-red-50 text-red-700 rounded-lg p-3 text-sm">
                {errorMessage}
              </div>
            )}
            {message.content && 
             !message.content.startsWith('Could not') && 
             !message.content.startsWith('Error code') && (
              <p className="text-sm italic text-slate-600 leading-relaxed">{message.content}</p>
            )}
            {message.sql && (
              <details className="text-sm">
                <summary className="cursor-pointer text-indigo-600 font-medium select-none">View SQL</summary>
                <pre className="mt-2 p-3 bg-slate-50 text-slate-700 rounded overflow-x-auto whitespace-pre-wrap">
                  {message.sql}
                </pre>
              </details>
            )}
            {message.chart_config && message.data && (
              <div className="mt-4 w-full h-[300px]">
                <ErrorBoundary>
                  <ChartRenderer chartConfig={{ ...message.chart_config, data: message.data }} />
                </ErrorBoundary>
              </div>
            )}
            {message.execution_time_ms !== undefined && (
              <div className="text-xs text-slate-400 mt-2 flex justify-between items-center">
                <div className="flex items-center gap-2">
                  <span>{message.row_count} rows retrieved</span>
                  {message.from_cache && (
                    <span className="text-xs text-slate-400 italic">⚡ cached</span>
                  )}
                  {message.data && message.data.length > 0 && message.columns && (
                    <button
                      onClick={() => exportToCSV(message.columns!, message.data!.map(row => message.columns!.map(c => row[c])), `export_${Date.now()}.csv`)}
                      className="ml-2 flex items-center text-indigo-500 hover:text-indigo-700 transition-colors"
                      title="Export to CSV"
                    >
                      <Download size={12} className="mr-1" /> Export
                    </button>
                  )}
                </div>
                <span>{message.execution_time_ms}ms</span>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default ChatMessage;
