import express from 'express';
import cors from 'cors';
import path from 'path';
import { fileURLToPath } from 'url';
import sessionRoutes from './routes/sessions';
import commandRoutes from './routes/commands';
import healthRoutes from './routes/health';
import { errorHandler } from './middleware/error-handler';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

export function createApp() {
  const app = express();

  app.use(cors());
  app.use(express.json());

  // API routes
  app.use('/api/sessions', sessionRoutes);
  app.use('/api/commands', commandRoutes);
  app.use('/api/health', healthRoutes);

  // Error handler (must be after routes)
  app.use(errorHandler);

  // In production, serve the built React app
  if (process.env.NODE_ENV === 'production') {
    const distPath = path.join(__dirname, '../../dist');
    app.use(express.static(distPath));
    app.get('*', (_req, res) => {
      res.sendFile(path.join(distPath, 'index.html'));
    });
  }

  return app;
}
