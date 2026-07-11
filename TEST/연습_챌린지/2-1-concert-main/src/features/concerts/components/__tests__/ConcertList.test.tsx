import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@/test/utils';
import { ConcertList } from '../ConcertList';
import { useConcertList } from '@/features/concerts/hooks/useConcertList';
import type { ConcertListItem } from '@/features/concerts/lib/dto';

vi.mock('@/features/concerts/hooks/useConcertList');
vi.mock('next/navigation', () => ({
  useRouter: vi.fn(() => ({
    push: vi.fn(),
    replace: vi.fn(),
    prefetch: vi.fn(),
    back: vi.fn(),
  })),
}));

const mockConcerts: ConcertListItem[] = [
  {
    id: '123e4567-e89b-12d3-a456-426614174001',
    title: '콘서트 1',
    description: '설명 1',
    eventDate: '2025-12-31T19:00:00Z',
    location: '서울',
    thumbnailUrl: 'https://picsum.photos/seed/concert1/400/300',
    totalSeats: 1000,
    reservedSeats: 500,
    availableSeats: 500,
    isSoldOut: false,
  },
  {
    id: '123e4567-e89b-12d3-a456-426614174002',
    title: '콘서트 2',
    description: '설명 2',
    eventDate: '2026-01-15T20:00:00Z',
    location: '부산',
    thumbnailUrl: 'https://picsum.photos/seed/concert2/400/300',
    totalSeats: 800,
    reservedSeats: 800,
    availableSeats: 0,
    isSoldOut: true,
  },
];

describe('ConcertList', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('로딩 중일 때 로딩 상태를 표시한다', () => {
    vi.mocked(useConcertList).mockReturnValue({
      data: undefined,
      isLoading: true,
      isError: false,
      error: null,
    } as any);

    render(<ConcertList />);

    // 스켈레톤 카드 존재 확인 (animate-pulse 클래스 확인)
    const skeletons = document.querySelectorAll('.animate-pulse');
    expect(skeletons.length).toBeGreaterThan(0);
  });

  it('에러 발생 시 에러 메시지를 표시한다', () => {
    const errorMessage = '네트워크 오류';
    vi.mocked(useConcertList).mockReturnValue({
      data: undefined,
      isLoading: false,
      isError: true,
      error: new Error(errorMessage),
    } as any);

    render(<ConcertList />);

    expect(
      screen.getByText(/콘서트 목록을 불러오는 중 오류가 발생했습니다/i)
    ).toBeInTheDocument();
    expect(screen.getByText(errorMessage)).toBeInTheDocument();
  });

  it('에러 상태에서 새로고침 버튼을 표시한다', () => {
    vi.mocked(useConcertList).mockReturnValue({
      data: undefined,
      isLoading: false,
      isError: true,
      error: new Error('오류'),
    } as any);

    render(<ConcertList />);

    const refreshButton = screen.getByRole('button', { name: /새로고침/i });
    expect(refreshButton).toBeInTheDocument();
  });

  it('콘서트 데이터가 없을 때 빈 상태를 표시한다', () => {
    vi.mocked(useConcertList).mockReturnValue({
      data: [],
      isLoading: false,
      isError: false,
      error: null,
    } as any);

    render(<ConcertList />);

    expect(screen.getByText(/현재 예약 가능한 콘서트가 없습니다/i)).toBeInTheDocument();
  });

  it('콘서트 목록을 렌더링한다', async () => {
    vi.mocked(useConcertList).mockReturnValue({
      data: mockConcerts,
      isLoading: false,
      isError: false,
      error: null,
    } as any);

    render(<ConcertList />);

    await waitFor(() => {
      expect(screen.getByText('콘서트 1')).toBeInTheDocument();
      expect(screen.getByText('콘서트 2')).toBeInTheDocument();
    });
  });

  it('각 콘서트 카드에 올바른 정보를 표시한다', async () => {
    vi.mocked(useConcertList).mockReturnValue({
      data: mockConcerts,
      isLoading: false,
      isError: false,
      error: null,
    } as any);

    render(<ConcertList />);

    await waitFor(() => {
      expect(screen.getByText('서울')).toBeInTheDocument();
      expect(screen.getByText('부산')).toBeInTheDocument();
      expect(screen.getByText('매진')).toBeInTheDocument();
    });
  });
});
