import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { ChatMessage } from '../types';

interface AppState {
  chatMessages: ChatMessage[];
  addMessage: (msg: ChatMessage) => void;
  clearMessages: () => void;
  
  selectedSource: string | null;
  setSelectedSource: (s: string) => void;
  
  selectedKpi: string | null;
  setSelectedKpi: (kpi: string | null) => void;
}

export const useAppStore = create<AppState>()(
  persist(
    (set) => ({
      chatMessages: [],
      addMessage: (msg) => set((state) => ({ chatMessages: [...state.chatMessages, msg] })),
      clearMessages: () => set({ chatMessages: [] }),
      
      selectedSource: null,
      setSelectedSource: (s) => set({ selectedSource: s }),
      
      selectedKpi: null,
      setSelectedKpi: (kpi) => set({ selectedKpi: kpi }),
    }),
    {
      name: 'primecon-storage',
      partialize: (state) => ({ chatMessages: state.chatMessages }),
      merge: (persistedState: any, currentState) => {
        const mergedMessages = persistedState?.chatMessages?.filter((m: any, i: number, arr: any[]) => 
          arr.findIndex((x: any) => x.id === m.id) === i
        ) || currentState.chatMessages;
        return {
          ...currentState,
          chatMessages: mergedMessages,
        };
      },
    }
  )
);
