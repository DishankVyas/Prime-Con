import { apiClient } from './client';

export const queryApi = {
  async getSuggestions(): Promise<string[]> {
    try {
      const response = await apiClient.get<string[]>('/api/query/suggestions');
      return response.data;
    } catch {
      // Return fallback suggestions if backend is slow to start
      return [
        'Show revenue by customer',
        'Top 5 overdue invoices',
        'Inventory value by plant',
        'Delayed production orders',
        'Sales orders created this week',
        'Purchase orders without goods receipt',
        'Average order to cash cycle time',
        'Scrap rate by material',
        'Highest value purchase orders',
        'Vendor on-time delivery rate',
        'Most frequently returned items',
        'Open AP amounts by vendor',
      ];
    }
  },

  async postQuery(question: string) {
    const response = await apiClient.post('/api/query', { question });
    return response.data;
  },

  streamQuery(
    question: string,
    onProgress: (stage: string, message: string) => void,
    onResult: (result: any) => void,
    onError: (err: string) => void
  ): () => void {
    const controller = new AbortController();
    // 60 second timeout for streaming queries (LLM can be slow)
    const timeoutId = setTimeout(() => controller.abort(), 60000);
    let fallbackTried = false;

    const runNonStreamFallback = async (reason: string) => {
      if (fallbackTried) {
        onError(reason);
        return;
      }
      fallbackTried = true;
      try {
        onProgress('fallback', 'Streaming timed out. Retrying without stream...');
        const result = await queryApi.postQuery(question);
        onResult(result);
      } catch (fallbackErr) {
        const msg = fallbackErr instanceof Error ? fallbackErr.message : reason;
        onError(msg);
      }
    };

    fetch('/api/query/stream', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Accept: 'text/event-stream',
      },
      body: JSON.stringify({ question }),
      signal: controller.signal,
    })
      .then(async (response) => {
        clearTimeout(timeoutId);
        if (!response.ok) {
          onError(`HTTP ${response.status}: ${response.statusText}`);
          return;
        }

        const reader = response.body!.getReader();
        const decoder = new TextDecoder();
        let buffer = '';
        let currentEvent = 'message';

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n');
          buffer = lines.pop() ?? '';

          for (const line of lines) {
            const trimmed = line.trim();

            if (trimmed.startsWith('event:')) {
              currentEvent = trimmed.slice(6).trim();
              continue;
            }

            if (trimmed.startsWith('data:')) {
              const raw = trimmed.slice(5).trim();
              if (!raw || raw === '[DONE]') continue;

              try {
                const parsed = JSON.parse(raw);
                if (currentEvent === 'progress') {
                  onProgress(parsed.stage ?? '', parsed.message ?? '');
                } else if (currentEvent === 'result') {
                  onResult(parsed);
                } else if (currentEvent === 'error') {
                  onError(parsed.error ?? 'Unknown error from server');
                }
              } catch {
                // ignore non-JSON lines
              }
              currentEvent = 'message';
            }
          }
        }
      })
      .catch((err: Error) => {
        clearTimeout(timeoutId);
        if (err.name !== 'AbortError') {
          void runNonStreamFallback(err.message);
        } else {
          void runNonStreamFallback('Request timed out after 60 seconds. Please try again.');
        }
      });

    return () => {
      clearTimeout(timeoutId);
      controller.abort();
    };
  },
};
