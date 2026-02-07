import { motion } from 'motion/react';
import type { ChatMessage, MessageGrouping } from '../../hooks/use-chat-session';
import { StreamingText } from './StreamingText';
import { ToolCallCard } from './ToolCallCard';
import { User, Bot } from 'lucide-react';
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
  const showAvatar = position === 'only' || position === 'first';
  const isGroupStart = position === 'only' || position === 'first';
  const isGroupEnd = position === 'only' || position === 'last';

  return (
    <motion.div
      initial={isNew ? { opacity: 0, y: 8 } : false}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2, ease: [0, 0, 0.2, 1] }}
      className={cn(
        'group relative flex gap-4 px-4 transition-colors duration-150',
        isGroupStart ? 'pt-4' : 'pt-0.5',
        isGroupEnd ? 'pb-3' : 'pb-0.5',
        isUser ? 'bg-muted/40 hover:bg-muted/50' : 'hover:bg-muted/20'
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
      <div className="flex-shrink-0 w-7">
        {showAvatar && (
          <div className="mt-1">
            {isUser ? (
              <div className="rounded-full bg-primary p-1.5">
                <User className="h-4 w-4 text-primary-foreground" />
              </div>
            ) : (
              <div className="rounded-full bg-[#C2724E] p-1.5">
                <Bot className="h-4 w-4 text-white" />
              </div>
            )}
          </div>
        )}
      </div>
      <div className="flex-1 min-w-0">
        <div className={isUser ? '' : 'max-w-[80ch]'}>
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
