import { motion } from 'motion/react';
import { ChevronRight } from 'lucide-react';
import type { ChatMessage, MessageGrouping } from '../../hooks/use-chat-session';
import { StreamingText } from './StreamingText';
import { ToolCallCard } from './ToolCallCard';
import { cn } from '../../lib/utils';

interface MessageItemProps {
  message: ChatMessage;
  grouping: MessageGrouping;
  isNew?: boolean;
  isStreaming?: boolean;
}

function formatTime(timestamp: string): string {
  try {
    return new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  } catch {
    return '';
  }
}

export function MessageItem({ message, grouping, isNew = false, isStreaming = false }: MessageItemProps) {
  const isUser = message.role === 'user';
  const { position, groupIndex } = grouping;
  const showIndicator = position === 'only' || position === 'first';
  const isGroupStart = position === 'only' || position === 'first';
  const isGroupEnd = position === 'only' || position === 'last';

  return (
    <motion.div
      initial={isNew ? { opacity: 0, y: 8 } : false}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2, ease: [0, 0, 0.2, 1] }}
      className={cn(
        'group relative flex gap-3 px-4 transition-colors duration-150',
        isGroupStart ? 'pt-4' : 'pt-0.5',
        isGroupEnd ? 'pb-3' : 'pb-0.5',
        isUser ? 'bg-user-msg hover:bg-user-msg/90' : 'hover:bg-muted/20'
      )}
    >
      {isGroupStart && groupIndex > 0 && (
        <div className="absolute inset-x-0 top-0 h-px bg-border/20" />
      )}
      {message.timestamp && (
        <span className="absolute right-4 top-1 text-xs text-muted-foreground/0 group-hover:text-muted-foreground/60 transition-colors duration-150">
          {formatTime(message.timestamp)}
        </span>
      )}
      <div className="flex-shrink-0 w-4 mt-[3px]">
        {showIndicator && (
          isUser ? (
            <ChevronRight className="h-4 w-4 text-muted-foreground" />
          ) : (
            <span className="flex items-center justify-center h-4 w-4 text-muted-foreground text-[10px]">●</span>
          )
        )}
      </div>
      <div className="flex-1 min-w-0 max-w-[80ch]">
        <div className={isUser ? '' : 'msg-assistant'}>
          {isUser ? (
            <div className="whitespace-pre-wrap break-words">{message.content}</div>
          ) : (
            <StreamingText content={message.content} isStreaming={isStreaming} />
          )}
        </div>
        {message.toolCalls?.map((tc) => (
          <ToolCallCard key={tc.toolCallId} toolCall={tc} />
        ))}
      </div>
    </motion.div>
  );
}
