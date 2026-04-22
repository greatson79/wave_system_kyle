'use client';

import Image from 'next/image';
import { format } from 'date-fns';
import { ko } from 'date-fns/locale';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Calendar, MapPin, Users } from 'lucide-react';
import type { ConcertListItem } from '@/features/concerts/lib/dto';

interface ConcertCardProps {
  concert: ConcertListItem;
  onClick: (concertId: string) => void;
}

export const ConcertCard = ({ concert, onClick }: ConcertCardProps) => {
  const eventDate = new Date(concert.eventDate);
  const formattedDate = format(eventDate, 'yyyy년 MM월 dd일 HH:mm', { locale: ko });

  return (
    <Card
      className="group cursor-pointer hover:-translate-y-1 hover:shadow-xl transition-all duration-300 border-[hsl(270,12%,88%)]"
      onClick={() => onClick(concert.id)}
    >
      {concert.thumbnailUrl && (
        <div className="aspect-[4/3] w-full overflow-hidden rounded-t-lg relative">
          <div className="absolute inset-0 bg-gradient-to-t from-black/30 to-transparent z-10" />
          <Image
            src={concert.thumbnailUrl}
            alt={concert.title}
            fill
            className="object-cover group-hover:scale-105 transition-transform duration-300"
            sizes="(max-width: 768px) 100vw, (max-width: 1024px) 50vw, 33vw"
          />
        </div>
      )}
      <CardHeader>
        <div className="flex items-start justify-between gap-2">
          <h3 className="text-xl font-bold line-clamp-2">{concert.title}</h3>
          {concert.isSoldOut && (
            <Badge className="bg-gradient-to-r from-[hsl(270,60%,50%)] to-[hsl(300,60%,60%)] text-white border-0">
              매진
            </Badge>
          )}
        </div>
      </CardHeader>
      <CardContent className="space-y-2">
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <Calendar className="w-4 h-4 text-[hsl(270,60%,50%)]" />
          <span>{formattedDate}</span>
        </div>
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <MapPin className="w-4 h-4 text-[hsl(270,60%,50%)]" />
          <span className="line-clamp-1">{concert.location}</span>
        </div>
        <div className="flex items-center gap-2 text-sm">
          <Users className="w-4 h-4 text-[hsl(270,60%,50%)]" />
          <span className="font-medium">
            {concert.reservedSeats}/{concert.totalSeats}명
          </span>
        </div>
      </CardContent>
    </Card>
  );
};
