'use client';

interface ConcertDescriptionProps {
  description: string | null;
}

export const ConcertDescription = ({ description }: ConcertDescriptionProps) => {
  if (!description) {
    return null;
  }

  return (
    <div className="space-y-2">
      <h3 className="text-lg font-semibold">상세 설명</h3>
      <p className="text-muted-foreground whitespace-pre-wrap">{description}</p>
    </div>
  );
};
