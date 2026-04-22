import { Hono } from 'hono';
import { errorBoundary } from '@/backend/middleware/error';
import { withAppContext } from '@/backend/middleware/context';
import { withSupabase } from '@/backend/middleware/supabase';
import { registerAuthRoutes } from '@/features/auth/backend/route';
import { registerCoursesRoutes } from '@/features/courses/backend/route';
import { registerDashboardRoutes } from '@/features/dashboard/backend/route';
import { registerAssignmentsRoutes } from '@/features/assignments/backend/route';
import { registerGradesRoutes } from '@/features/grades/backend/route';
import { registerReportsRoutes } from '@/features/reports/backend/route';
import { registerMetadataRoutes } from '@/features/metadata/backend/route';
import { registerExampleRoutes } from '@/features/example/backend/route';
import { registerProfileRoutes } from '@/features/profile/backend/route';
import type { AppEnv } from '@/backend/hono/context';

let singletonApp: Hono<AppEnv> | null = null;

export const createHonoApp = () => {
  if (singletonApp && process.env.NODE_ENV === 'production') {
    return singletonApp;
  }

  const app = new Hono<AppEnv>();

  app.use('*', errorBoundary());
  app.use('*', withAppContext());
  app.use('*', withSupabase());

  registerAuthRoutes(app);
  registerProfileRoutes(app);
  registerCoursesRoutes(app);
  registerDashboardRoutes(app);
  registerAssignmentsRoutes(app);
  registerGradesRoutes(app);
  registerReportsRoutes(app);
  registerMetadataRoutes(app);
  registerExampleRoutes(app);

  app.notFound((c) => {
    return c.json(
      {
        error: {
          code: 'NOT_FOUND',
          message: `Route not found: ${c.req.method} ${c.req.path}`,
        },
      },
      404,
    );
  });

  if (process.env.NODE_ENV === 'production') {
    singletonApp = app;
  }

  return app;
};
