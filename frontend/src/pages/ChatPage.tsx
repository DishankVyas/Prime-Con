import React, { useEffect, useRef, useState } from 'react';
import { Send } from 'lucide-react';
import { useAppStore } from '../store/appStore';
import { queryApi } from '../api/queryApi';
import ChatMessage from '../components/ChatMessage';
import LoadingDots from '../components/LoadingDots';

const generateId = () => Math.random().toString(36).substring(2, 9);

const ChatPage: React.FC = () => {
  const { chatMessages, addMessage } = useAppStore();
  const [input, setInput] = useState('');
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [streamingStage, setStreamingStage] = useState<string | null>(null);
  const endOfMessagesRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    queryApi.getSuggestions().then(setSuggestions).catch(console.error);
  }, []);

  useEffect(() => {
    endOfMessagesRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatMessages, isLoading]);

  const handleSend = async (text: string) => {
    if (!text.trim() || isLoading) return;
    
    addMessage({ id: generateId(), role: 'user', content: text });
    setInput('');
    setIsLoading(true);

    const stopStream = queryApi.streamQuery(
      text,
      (stage, message) => setStreamingStage(message),
      (result) => {
        setStreamingStage(null);
        addMessage({
          id: generateId(),
          role: 'assistant',
          content: result.ai_summary || null,
          sql: result.sql,
          chart_config: result.chart_config,
          data: result.data,
          execution_time_ms: result.execution_time_ms,
          row_count: result.row_count,
        });
        setIsLoading(false);
      },
      (err) => {
        setStreamingStage(null);
        const errorMessage =
          typeof err === 'string'
            ? err
            : 'Failed to connect to the backend. Please ensure the app is running.';
        addMessage({ id: generateId(), role: 'assistant', content: null, error: errorMessage } as any);
        setIsLoading(false);
      }
    );
  };

  return (
    <div className="flex flex-col h-full bg-slate-50 relative">
      <div className="flex-1 overflow-y-auto p-6 pb-32">
        {chatMessages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center space-y-8">
            <div>
              <h1 className="text-3xl font-bold text-slate-800 mb-2">PrimeConSemLayer</h1>
              <p className="text-slate-500">Ask anything about your SAP data</p>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 max-w-2xl w-full">
              {suggestions.slice(0, 4).map((s, i) => (
                <button
                  key={i}
                  onClick={() => {
                    const mockMap: Record<string, string> = {
                      "Show revenue by customer": "revenue by customer",
                      "Top 5 overdue invoices": "top 5 overdue",
                      "Open AP amounts by vendor": "open ap",
                      "Inventory value by plant": "inventory value by plant",
                      "Delayed production orders": "delayed production",
                      "Sales orders created this week": "sales orders this week",
                      "Purchase orders without goods receipt": "purchase orders without goods",
                      "Average order to cash cycle time": "average order to cash",
                      "Scrap rate by material": "scrap rate by material",
                      "Highest value purchase orders": "highest value purchase",
                      "Vendor on-time delivery rate": "vendor on-time",
                      "Most frequently returned items": "returned items",
                    };
                    handleSend(mockMap[s] || s);
                  }}
                  className="bg-white border border-slate-200 rounded-xl p-4 text-left text-sm text-slate-700 hover:border-indigo-300 hover:shadow-md transition-all"
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <div className="max-w-4xl mx-auto flex flex-col items-center">
            {chatMessages.map(msg => (
              <ChatMessage key={msg.id} message={msg} />
            ))}
            {isLoading && (
              <div className="flex w-full mb-6 justify-start">
                <div className="bg-white border border-slate-200 rounded-2xl shadow-sm px-6 py-4 flex items-center space-x-3">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-indigo-600"></div>
                  <span className="text-sm text-slate-500">{streamingStage || 'Thinking...'}</span>
                </div>
              </div>
            )}
            <div ref={endOfMessagesRef} />
          </div>
        )}
      </div>

      <div className="absolute bottom-0 left-0 w-full bg-gradient-to-t from-slate-50 via-slate-50 to-transparent p-6 pt-10">
        <div className="max-w-4xl mx-auto relative flex items-center">
          <textarea
            className="w-full bg-white border border-slate-300 rounded-2xl pl-6 pr-14 py-4 focus:outline-none focus:ring-2 focus:ring-indigo-500 shadow-lg resize-none min-h-[56px] max-h-32"
            rows={1}
            placeholder="Ask a question about your business data..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                handleSend(input);
              }
            }}
          />
          <button
            onClick={() => handleSend(input)}
            disabled={!input.trim() || isLoading}
            className="absolute right-3 bg-indigo-600 text-white p-2.5 rounded-xl hover:bg-indigo-700 disabled:opacity-50 transition-colors"
          >
            <Send size={20} />
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatPage;
