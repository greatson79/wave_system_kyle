import { z } from 'zod';

export const NotificationSchema = z.object({
  id: z.string().uuid(),
  userId: z.string().uuid(),
  type: z.string(),
  title: z.string(),
  content: z.string(),
  isRead: z.boolean(),
  createdAt: z.string(),
});

export type Notification = z.infer<typeof NotificationSchema>;
