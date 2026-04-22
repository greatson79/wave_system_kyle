import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen } from '@/test/utils';
import userEvent from '@testing-library/user-event';
import { SeatCard } from '../SeatCard';
import { useSeatSelectionStore } from '../../stores/useSeatSelectionStore';
import type { Seat } from '../../backend/schema';

const mockAvailableSeat: Seat = {
  id: '123e4567-e89b-12d3-a456-426614174001',
  section: 'A',
  row: 1,
  seatColumn: 1,
  isReserved: false,
};

const mockReservedSeat: Seat = {
  id: '123e4567-e89b-12d3-a456-426614174002',
  section: 'A',
  row: 1,
  seatColumn: 2,
  isReserved: true,
};

describe('SeatCard', () => {
  beforeEach(() => {
    useSeatSelectionStore.getState().clearSeats();
  });

  afterEach(() => {
    useSeatSelectionStore.getState().clearSeats();
  });

  it('좌석 정보를 올바르게 렌더링한다', () => {
    render(<SeatCard seat={mockAvailableSeat} />);

    expect(screen.getByText('1-1')).toBeInTheDocument();
    expect(
      screen.getByLabelText(/A구역 1행 1열 예약 가능/i)
    ).toBeInTheDocument();
  });

  it('예약 가능한 좌석을 클릭하면 선택된다', async () => {
    const user = userEvent.setup();
    render(<SeatCard seat={mockAvailableSeat} />);

    const button = screen.getByRole('button');
    await user.click(button);

    const store = useSeatSelectionStore.getState();
    expect(store.selectedSeats).toHaveLength(1);
    expect(store.selectedSeats[0].id).toBe(mockAvailableSeat.id);
  });

  it('선택된 좌석을 다시 클릭하면 선택이 해제된다', async () => {
    const user = userEvent.setup();
    useSeatSelectionStore.getState().addSeat(mockAvailableSeat);

    render(<SeatCard seat={mockAvailableSeat} />);

    const button = screen.getByRole('button');
    await user.click(button);

    const store = useSeatSelectionStore.getState();
    expect(store.selectedSeats).toHaveLength(0);
  });

  it('예약된 좌석은 비활성화된다', () => {
    render(<SeatCard seat={mockReservedSeat} />);

    const button = screen.getByRole('button');
    expect(button).toBeDisabled();
    expect(screen.getByLabelText(/예약됨/i)).toBeInTheDocument();
  });

  it('예약된 좌석을 클릭해도 선택되지 않는다', async () => {
    const user = userEvent.setup();
    render(<SeatCard seat={mockReservedSeat} />);

    const button = screen.getByRole('button');
    await user.click(button);

    const store = useSeatSelectionStore.getState();
    expect(store.selectedSeats).toHaveLength(0);
  });

  it('최대 4석 선택 시 추가 선택이 불가능하다', async () => {
    const user = userEvent.setup();
    const alertSpy = vi.spyOn(window, 'alert').mockImplementation(() => {});

    // 4석 미리 선택
    const seats: Seat[] = [
      { id: '1', section: 'A', row: 1, seatColumn: 1, isReserved: false },
      { id: '2', section: 'A', row: 1, seatColumn: 2, isReserved: false },
      { id: '3', section: 'A', row: 1, seatColumn: 3, isReserved: false },
      { id: '4', section: 'A', row: 1, seatColumn: 4, isReserved: false },
    ];

    seats.forEach((seat) => useSeatSelectionStore.getState().addSeat(seat));

    const fifthSeat: Seat = {
      id: '5',
      section: 'A',
      row: 2,
      seatColumn: 1,
      isReserved: false,
    };

    render(<SeatCard seat={fifthSeat} />);

    const button = screen.getByRole('button');
    await user.click(button);

    expect(alertSpy).toHaveBeenCalledWith('최대 4석까지만 선택할 수 있습니다.');
    expect(useSeatSelectionStore.getState().selectedSeats).toHaveLength(4);

    alertSpy.mockRestore();
  });

  it('선택된 좌석은 시각적으로 구분된다', () => {
    useSeatSelectionStore.getState().addSeat(mockAvailableSeat);

    render(<SeatCard seat={mockAvailableSeat} />);

    const button = screen.getByRole('button');
    expect(button).toHaveClass('bg-blue-500');
    expect(screen.getByLabelText(/선택됨/i)).toBeInTheDocument();
  });
});
