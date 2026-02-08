import type { StreamEvent } from '../shared/types';
/**
 * Creates an AsyncGenerator that yields StreamEvent objects.
 * Used to mock agentManager.sendMessage().
 */
export declare function mockStreamGenerator(events: StreamEvent[]): AsyncGenerator<StreamEvent>;
/**
 * Parses raw SSE text (as sent over the wire) into structured events.
 * Used to assert on supertest response bodies.
 */
export declare function parseSSEResponse(text: string): Array<{
    type: string;
    data: unknown;
}>;
//# sourceMappingURL=sse-helpers.d.ts.map