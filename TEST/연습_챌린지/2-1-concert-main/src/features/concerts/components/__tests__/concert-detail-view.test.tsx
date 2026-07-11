import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@/test/utils';
import { ConcertDetailView } from '../concert-detail-view';
import { useConcertDetailQuery } from '../../hooks/useConcertDetailQuery';
import type { ConcertDetailResponse } from '@/features/concerts/lib/dto';

vi.mock('../../hooks/useConcertDetailQuery');
vi.mock('next/navigation', () => ({
  useRouter: vi.fn(() => ({
    push: vi.fn(),
    replace: vi.fn(),
    back: vi.fn(),
  })),
}));

const mockConcertDetail: ConcertDetailResponse = {
  id: '123e4567-e89b-12d3-a456-426614174000',
  title: '테스트 콘서트',
  description: '멋진 콘서트입니다',
  eventDate: '2025-12-31T19:00:00Z',
  location: '서울 올림픽공원',
  thumbnailUrl: 'https://picsum.photos/seed/concert1/800/600',
  performers: ['아티스트 A', '아티스트 B'],
  totalSeats: 1000,
  reservedSeats: 500,
  availableSeats: 500,
  isSoldOut: false,
  isBookable: true,
  bookingDeadline: '2025-12-30T23:59:59Z',
  createdAt: '2025-10-01T00:00:00Z',
};

describe('ConcertDetailView', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('로딩 중일 때 스켈레톤을 표시한다', () => {
    vi.mocked(useConcertDetailQuery).mockReturnValue({
      data: undefined,
      isLoading: true,
      isError: false,
      error: null,
    } as any);

    render(<ConcertDetailView concertId="test-id" />);

    expect(screen.getByTestId('concert-detail-skeleton')).toBeInTheDocument();
  });

  it('에러 발생 시 에러 메시지를 표시한다', () => {
    vi.mocked(useConcertDetailQuery).mockReturnValue({
      data: undefined,
      isLoading: false,
      isError: true,
      error: new Error('콘서트를 찾을 수 없습니다'),
    } as any);

    render(<ConcertDetailView concertId="test-id" />);

    expect(screen.getByRole('heading', { name: '콘서트를 찾을 수 없습니다' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /돌아가기/i })).toBeInTheDocument();
  });

  it('콘서트 상세 정보를 렌더링한다', async () => {
    vi.mocked(useConcertDetailQuery).mockReturnValue({
      data: mockConcertDetail,
      isLoading: false,
      isError: false,
      error: null,
    } as any);

    render(<ConcertDetailView concertId="test-id" />);

    await waitFor(() => {
      expect(screen.getByText('테스트 콘서트')).toBeInTheDocument();
      expect(screen.getByText('멋진 콘서트입니다')).toBeInTheDocument();
      expect(screen.getByText('서울 올림픽공원')).toBeInTheDocument();
    });
  });

  it('예약 가능할 때 예약 버튼을 표시한다', async () => {
    vi.mocked(useConcertDetailQuery).mockReturnValue({
      data: mockConcertDetail,
      isLoading: false,
      isError: false,
      error: null,
    } as any);

    render(<ConcertDetailView concertId="test-id" />);

    await waitFor(() => {
      const bookingButton = screen.getByRole('button', { name: /예약하기/i });
      expect(bookingButton).toBeInTheDocument();
      expect(bookingButton).not.toBeDisabled();
    });
  });

  it('매진일 때 예약 버튼을 비활성화한다', async () => {
    const soldOutConcert = { ...mockConcertDetail, isSoldOut: true, isBookable: false };
    vi.mocked(useConcertDetailQuery).mockReturnValue({
      data: soldOutConcert,
      isLoading: false,
      isError: false,
      error: null,
    } as any);

    render(<ConcertDetailView concertId="test-id" />);

    await waitFor(() => {
      const bookingButton = screen.getByRole('button', { name: /매진/i });
      expect(bookingButton).toBeDisabled();
    });
  });

  it('예약 정보를 표시한다', async () => {
    vi.mocked(useConcertDetailQuery).mockReturnValue({
      data: mockConcertDetail,
      isLoading: false,
      isError: false,
      error: null,
    } as any);

    render(<ConcertDetailView concertId="test-id" />);

    await waitFor(() => {
      // 좌석 정보가 렌더링되는지 확인
      expect(screen.getByText(mockConcertDetail.title)).toBeInTheDocument();
      expect(screen.getByText(mockConcertDetail.location)).toBeInTheDocument();
    });
  });
});
