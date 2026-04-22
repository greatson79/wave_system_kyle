import { NextRequest, NextResponse } from 'next/server';
import { createPureClient } from '@/lib/supabase/server';
import { autoCloseAssignments } from '@/features/assignments/backend/auto-close';
import type { ErrorResult } from '@/backend/http/response';

export const runtime = 'nodejs';

/**
 * Vercel Cron으로 호출되는 자동 마감 핸들러
 *
 * vercel.json 설정 예시:
 * {
 *   "crons": [
 *     {
 *       "path": "/api/cron/auto-close-assignments",
 *       "schedule": "0 * * * *"
 *     }
 *   ]
 * }
 */
export async function GET(request: NextRequest) {
  const logger = {
    info: console.info,
    error: console.error,
    warn: console.warn,
    debug: console.debug,
  };

  // Cron Secret 검증 (보안)
  const authHeader = request.headers.get('authorization');
  const cronSecret = process.env.CRON_SECRET;

  if (cronSecret && authHeader !== `Bearer ${cronSecret}`) {
    logger.warn('Unauthorized cron request');
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  logger.info('Auto close assignments cron job started');

  try {
    const supabase = await createPureClient();
    const result = await autoCloseAssignments(supabase);

    if (result.ok) {
      logger.info('Auto close completed', {
        closedCount: result.data.closedCount,
        closedIds: result.data.closedAssignmentIds,
      });

      return NextResponse.json(
        {
          success: true,
          closedCount: result.data.closedCount,
          closedAssignmentIds: result.data.closedAssignmentIds,
          message: result.data.message,
        },
        { status: 200 },
      );
    }

    const errorResult = result as ErrorResult<string>;
    logger.error('Auto close failed', { error: errorResult.error });
    return NextResponse.json(
      { error: errorResult.error.message },
      { status: errorResult.status },
    );
  } catch (err) {
    logger.error('Unexpected error in auto close cron', { error: err });
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 },
    );
  }
}
