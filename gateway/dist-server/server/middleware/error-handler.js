export function errorHandler(err, _req, res, _next) {
    console.error('[Gateway Error]', err.message, err.stack);
    res.status(500).json({
        error: err.message || 'Internal Server Error',
        code: 'INTERNAL_ERROR',
    });
}
//# sourceMappingURL=error-handler.js.map