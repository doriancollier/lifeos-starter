import { useCallback } from 'react';
import { getPlatform } from '../../client/lib/platform';

export function useFileOpener() {
  const openFile = useCallback(async (path: string) => {
    await getPlatform().openFile(path);
  }, []);
  return { openFile };
}
