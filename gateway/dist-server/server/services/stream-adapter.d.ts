import type { Response } from 'express';
import type { StreamEvent } from '../../shared/types.js';
export declare function initSSEStream(res: Response): void;
export declare function sendSSEEvent(res: Response, event: StreamEvent): void;
export declare function endSSEStream(res: Response): void;
//# sourceMappingURL=stream-adapter.d.ts.map