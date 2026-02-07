import { useQuery } from '@tanstack/react-query';
import { api } from '../lib/api';
import type { CommandRegistry } from '@shared/types';

export function useCommands() {
  return useQuery<CommandRegistry>({
    queryKey: ['commands'],
    queryFn: () => api.getCommands(),
    staleTime: 5 * 60 * 1000,
    gcTime: 30 * 60 * 1000,
  });
}

export function useRefreshCommands() {
  return useQuery<CommandRegistry>({
    queryKey: ['commands', 'refresh'],
    queryFn: () => api.getCommands(true),
    enabled: false,
  });
}
