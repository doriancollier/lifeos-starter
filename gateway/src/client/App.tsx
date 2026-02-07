import { useAppStore } from './stores/app-store';
import { motion, MotionConfig } from 'motion/react';
import { Header } from './components/layout/Header';
import { PermissionBanner } from './components/layout/PermissionBanner';
import { SessionSidebar } from './components/sessions/SessionSidebar';
import { ChatPanel } from './components/chat/ChatPanel';

export function App() {
  const { activeSessionId, sidebarOpen } = useAppStore();

  return (
    <MotionConfig reducedMotion="user">
      <div className="flex flex-col h-screen bg-background text-foreground">
        <PermissionBanner sessionId={activeSessionId} />
        <Header />
        <div className="flex flex-1 overflow-hidden">
          <motion.div
            animate={{ width: sidebarOpen ? 256 : 0 }}
            transition={{ duration: 0.2, ease: [0, 0, 0.2, 1] }}
            className="overflow-hidden flex-shrink-0 border-r"
          >
            <div className="w-64 h-full overflow-y-auto">
              <SessionSidebar />
            </div>
          </motion.div>
          <main className="flex-1 overflow-hidden">
            {activeSessionId ? (
              <ChatPanel key={activeSessionId} sessionId={activeSessionId} />
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
