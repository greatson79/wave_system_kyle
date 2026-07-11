'use client';

import Image from 'next/image';
import { Music } from 'lucide-react';

interface ConcertThumbnailProps {
  src: string | null;
  alt: string;
}

export const ConcertThumbnail = ({ src, alt }: ConcertThumbnailProps) => {
  if (!src) {
    return (
      <div className="w-full aspect-[21/9] bg-gradient-to-br from-primary/20 to-purple-200 flex items-center justify-center">
        <Music className="h-24 w-24 text-primary/40" />
      </div>
    );
  }

  return (
    <div className="w-full aspect-[21/9] relative overflow-hidden shadow-lg group">
      <Image
        src={src}
        alt={alt}
        fill
        className="object-cover transition-transform duration-300 group-hover:scale-105"
        priority
      />
      {/* Gradient Overlay */}
      <div className="absolute inset-0 bg-gradient-to-t from-black/30 via-transparent to-transparent" />
    </div>
  );
};
