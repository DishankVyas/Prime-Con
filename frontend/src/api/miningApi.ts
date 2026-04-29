import { apiClient } from './client';
import { MiningSourceResponse, MiningDiscoverResponse, TaskStatusResponse } from '../types';

export const miningApi = {
  getSources: async () => {
    const { data } = await apiClient.get<MiningSourceResponse[]>('/api/mining/sources');
    return data;
  },
  discover: async (source: string, startDate?: string, endDate?: string) => {
    const { data } = await apiClient.post<MiningDiscoverResponse>('/api/mining/discover', { 
      source, 
      start_date: startDate, 
      end_date: endDate 
    });
    return data;
  },
  getTaskStatus: async (taskId: string) => {
    const { data } = await apiClient.get<TaskStatusResponse>(`/api/mining/task/${taskId}`);
    return data;
  }
};
