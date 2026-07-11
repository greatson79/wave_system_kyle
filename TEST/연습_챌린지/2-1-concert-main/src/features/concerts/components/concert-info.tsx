'use client';

import { Calendar, MapPin } from 'lucide-react';
import { formatConcertDate } from '@/lib/utils';
import type { ConcertDetailResponse } from '../lib/dto';

interface ConcertInfoProps {
  concert: ConcertDetailResponse;
}

export const ConcertInfo = ({ concert }: ConcertInfoProps) => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-4xl font-bold text-neutral-900 mb-2">{concert.title}</h1>
      </div>

      <div className="flex flex-col gap-4 p-6 border-2 border-neutral-200 rounded-xl shadow-md bg-white">
        <div className="flex items-center gap-3">
          <div className="flex items-center justify-center w-10 h-10 rounded-lg bg-primary/10">
            <Calendar className="h-5 w-5 text-primary" />
          </div>
          <div>
            <p className="text-xs font-semibold text-neutral-500 uppercase">일시</p>
            <p className="text-base font-semibold text-neutral-900">{formatConcertDate(concert.eventDate)}</p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex items-center justify-center w-10 h-10 rounded-lg bg-primary/10">
            <MapPin className="h-5 w-5 text-primary" />
          </div>
          <div>
            <p className="text-xs font-semibold text-neutral-500 uppercase">장소</p>
            <p className="text-base font-semibold text-neutral-900">{concert.location}</p>
          </div>
        </div>
      </div>
    </div>
  );
};
