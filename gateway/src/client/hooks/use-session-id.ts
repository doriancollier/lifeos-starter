import { useQueryState } from 'nuqs';

export function useSessionId() {
  return useQueryState('session');
}
