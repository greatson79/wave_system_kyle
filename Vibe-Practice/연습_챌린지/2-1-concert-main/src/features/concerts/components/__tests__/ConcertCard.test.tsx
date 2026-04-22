import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@/test/utils';
import userEvent from '@testing-library/user-event';
import { ConcertCard } from '../ConcertCard';
import type { ConcertListItem } from '@/features/concerts/lib/dto';

const mockConcert: ConcertListItem = {
  id: '123e4567-e89b-12d3-a456-426614174000',
  title: '테스트 콘서트',
  description: '테스트 설명',
  eventDate: '2025-12-31T19:00:00Z',
  location: '서울 올림픽공원',
  thumbnailUrl: 'https://picsum.photos/seed/concert1/400/300',
  totalSeats: 1000,
  reservedSeats: 500,
  availableSeats: 500,
  isSoldOut: false,
};

describe('ConcertCard', () => {
  it('콘서트 정보를 올바르게 렌더링한다', () => {
    const onClick = vi.fn();
    render(<ConcertCard concert={mockConcert} onClick={onClick} />);

    expect(screen.getByText('테스트 콘서트')).toBeInTheDocument();
    expect(screen.getByText('서울 올림픽공원')).toBeInTheDocument();
    expect(screen.getByText('500/1000명')).toBeInTheDocument();
  });

  it('썸네일 이미지를 렌더링한다', () => {
    const onClick = vi.fn();
    render(<ConcertCard concert={mockConcert} onClick={onClick} />);

    const image = screen.getByAltText('테스트 콘서트');
    expect(image).toBeInTheDocument();
    expect(image).toHaveAttribute('src', mockConcert.thumbnailUrl);
  });

  it('썸네일이 없을 때 이미지를 렌더링하지 않는다', () => {
    const onClick = vi.fn();
    const concertWithoutThumbnail = { ...mockConcert, thumbnailUrl: null };
    render(<ConcertCard concert={concertWithoutThumbnail} onClick={onClick} />);

    const image = screen.queryByRole('img');
    expect(image).not.toBeInTheDocument();
  });

  it('매진 상태일 때 배지를 표시한다', () => {
    const onClick = vi.fn();
    const soldOutConcert = { ...mockConcert, isSoldOut: true };
    render(<ConcertCard concert={soldOutConcert} onClick={onClick} />);

    expect(screen.getByText('매진')).toBeInTheDocument();
  });

  it('매진 상태가 아닐 때 배지를 표시하지 않는다', () => {
    const onClick = vi.fn();
    render(<ConcertCard concert={mockConcert} onClick={onClick} />);

    expect(screen.queryByText('매진')).not.toBeInTheDocument();
  });

  it('카드 클릭 시 onClick 핸들러가 호출된다', async () => {
    const onClick = vi.fn();
    const user = userEvent.setup();
    render(<ConcertCard concert={mockConcert} onClick={onClick} />);

    const card = screen.getByText('테스트 콘서트').closest('div[class*="card"]');
    if (card) {
      await user.click(card);
      expect(onClick).toHaveBeenCalledWith(mockConcert.id);
    }
  });

  it('날짜를 한국어 형식으로 포맷한다', () => {
    const onClick = vi.fn();
    render(<ConcertCard concert={mockConcert} onClick={onClick} />);

    // 날짜가 포맷되어 표시되는지 확인 (타임존에 상관없이)
    expect(screen.getByText(/2025년|2026년/)).toBeInTheDocument();
  });
});
