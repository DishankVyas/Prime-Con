import { apiClient } from './client';
import { KpiData, RcaResponse } from '../types';

export const kpiApi = {
  getAll: async () => {
    const { data } = await apiClient.get<KpiData[]>('/api/kpi/all');
    return data;
  },
  getModules: async () => {
    const { data } = await apiClient.get('/api/kpi/modules');
    return data;
  },
  getRca: async (kpiId: string) => {
    const { data } = await apiClient.get<RcaResponse>(`/api/kpi/rca/${kpiId}`);
    return data;
  }
};
