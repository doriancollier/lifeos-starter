import { useState, useEffect } from 'react';
import { getPlatform } from '../../client/lib/platform';

export function ConnectionStatus() {
  const [connected, setConnected] = useState<boolean | null>(null);

  useEffect(() => {
    const check = async () => {
      try {
        const res = await fetch(`${getPlatform().apiBaseUrl}/health`);
        setConnected(res.ok);
      } catch {
        setConnected(false);
      }
    };
    check();
    const interval = setInterval(check, 30_000);
    return () => clearInterval(interval);
  }, []);

  if (connected === null) return null;
  if (connected) return null;

  return (
    <div className="px-3 py-2 text-xs text-center border-b bg-destructive/10 text-destructive">
      Gateway not connected. Run the server on port 6942.
    </div>
  );
}
