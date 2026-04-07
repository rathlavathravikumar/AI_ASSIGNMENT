import { app } from './app.js';
import { connectDb } from './config/db.js';
import { env } from './config/env.js';

async function boot() {
  try {
    await connectDb();
    app.listen(env.port, () => {
      console.log(`API running on http://localhost:${env.port}`);
    });
  } catch (error) {
    console.error('Boot failure:', error.message);
    process.exit(1);
  }
}

boot();
