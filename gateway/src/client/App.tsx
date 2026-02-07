import { useEffect, useRef } from 'react';
import { useAppStore } from './stores/app-store';
import { useSessionId } from './hooks/use-session-id';
import { useIsMobile } from './hooks/use-is-mobile';
import { motion, AnimatePresence, MotionConfig } from 'motion/react';
import { PanelLeft } from 'lucide-react';
import { PermissionBanner } from './components/layout/PermissionBanner';
import { SessionSidebar } from './components/sessions/SessionSidebar';
import { ChatPanel } from './components/chat/ChatPanel';

interface AppProps {
  /** Optional transform applied to message content before sending to server */
  transformContent?: (content: string) => string | Promise<string>;
  /** When true, hides sidebar and uses container-relative sizing (for Obsidian) */
  embedded?: boolean;
}

export function App({ transformContent, embedded }: AppProps = {}) {
  const { sidebarOpen, setSidebarOpen, toggleSidebar } = useAppStore();
  const [activeSessionId] = useSessionId();
  const isMobile = useIsMobile();
  const containerRef = useRef<HTMLDivElement>(null);

  // Escape key closes mobile overlay — scoped to container when embedded
  useEffect(() => {
    if (embedded) return; // embedded mode has no sidebar overlay
    if (!isMobile || !sidebarOpen) return;
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setSidebarOpen(false);
    };
    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [embedded, isMobile, sidebarOpen, setSidebarOpen]);

  // Embedded mode: no sidebar, just the chat panel
  if (embedded) {
    return (
      <MotionConfig reducedMotion="user">
        <div className="flex flex-col h-full bg-background text-foreground">
          <PermissionBanner sessionId={activeSessionId} />
          <main className="flex-1 overflow-hidden">
            {activeSessionId ? (
              <ChatPanel key={activeSessionId} sessionId={activeSessionId} transformContent={transformContent} />
            ) : (
              <div className="flex-1 flex items-center justify-center h-full">
                <div className="text-center">
                  <p className="text-muted-foreground text-base">New conversation</p>
                  <p className="text-muted-foreground/60 text-sm mt-2">
                    Select a session or start a new one
                  </p>
                </div>
              </div>
            )}
          </main>
        </div>
      </MotionConfig>
    );
  }

  return (
    <MotionConfig reducedMotion="user">
      <div ref={containerRef} className="flex flex-col h-screen bg-background text-foreground">
        <PermissionBanner sessionId={activeSessionId} />
        <div className="relative flex flex-1 overflow-hidden">
          {/* Floating toggle — visible when sidebar is closed */}
          <AnimatePresence>
            {!sidebarOpen && (
              <motion.button
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.9 }}
                transition={{ duration: 0.15, ease: [0, 0, 0.2, 1] }}
                onClick={toggleSidebar}
                className="absolute top-3 left-3 z-30 p-1.5 rounded-md bg-background/80 backdrop-blur border shadow-sm hover:bg-accent transition-colors duration-150"
                aria-label="Open sidebar"
              >
                <PanelLeft className="h-4 w-4" />
              </motion.button>
            )}
          </AnimatePresence>

          {isMobile ? (
            /* Mobile: overlay sidebar with backdrop */
            <AnimatePresence>
              {sidebarOpen && (
                <>
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    transition={{ duration: 0.2 }}
                    className="fixed inset-0 z-40 bg-black/40"
                    onClick={() => setSidebarOpen(false)}
                    aria-label="Close sidebar"
                  />
                  <motion.div
                    initial={{ x: -256 }}
                    animate={{ x: 0 }}
                    exit={{ x: -256 }}
                    transition={{ duration: 0.2, ease: [0, 0, 0.2, 1] }}
                    className="fixed top-0 left-0 z-50 h-full w-64 border-r bg-background overflow-y-auto"
                  >
                    <SessionSidebar />
                  </motion.div>
                </>
              )}
            </AnimatePresence>
          ) : (
            /* Desktop: push sidebar */
            <motion.div
              animate={{ width: sidebarOpen ? 256 : 0 }}
              transition={{ duration: 0.2, ease: [0, 0, 0.2, 1] }}
              className="overflow-hidden flex-shrink-0 border-r"
            >
              <div className="w-64 h-full overflow-y-auto">
                <SessionSidebar />
              </div>
            </motion.div>
          )}

          <main className="flex-1 overflow-hidden">
            {activeSessionId ? (
              <ChatPanel key={activeSessionId} sessionId={activeSessionId} transformContent={transformContent} />
            ) : (
              <div className="flex-1 flex items-center justify-center h-full">
                <div className="text-center">
                  <p className="text-muted-foreground text-base">New conversation</p>
                  <p className="text-muted-foreground/60 text-sm mt-2">
                    Select a session or start a new one
                  </p>
                </div>
              </div>
            )}
          </main>
        </div>
      </div>
    </MotionConfig>
  );
}
