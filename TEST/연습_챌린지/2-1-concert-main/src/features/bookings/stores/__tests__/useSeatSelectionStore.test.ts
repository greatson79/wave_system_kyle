import { describe, it, expect, beforeEach } from 'vitest';
import { useSeatSelectionStore } from '../useSeatSelectionStore';
import type { Seat } from '../../backend/schema';

const createMockSeat = (id: string, row: number, column: number): Seat => ({
  id,
  section: 'A',
  row,
  seatColumn: column,
  isReserved: false,
});

describe('useSeatSelectionStore', () => {
  beforeEach(() => {
    useSeatSelectionStore.getState().clearSeats();
  });

  describe('addSeat', () => {
    it('좌석을 추가할 수 있다', () => {
      const seat = createMockSeat('seat-1', 1, 1);
      useSeatSelectionStore.getState().addSeat(seat);

      expect(useSeatSelectionStore.getState().selectedSeats).toHaveLength(1);
      expect(useSeatSelectionStore.getState().selectedSeats[0].id).toBe('seat-1');
    });

    it('이미 선택된 좌석은 중복 추가되지 않는다', () => {
      const seat = createMockSeat('seat-1', 1, 1);

      useSeatSelectionStore.getState().addSeat(seat);
      useSeatSelectionStore.getState().addSeat(seat);

      expect(useSeatSelectionStore.getState().selectedSeats).toHaveLength(1);
    });

    it('최대 4석까지만 선택할 수 있다', () => {
      const seats = [
        createMockSeat('seat-1', 1, 1),
        createMockSeat('seat-2', 1, 2),
        createMockSeat('seat-3', 1, 3),
        createMockSeat('seat-4', 1, 4),
        createMockSeat('seat-5', 2, 1),
      ];

      seats.forEach((seat) => useSeatSelectionStore.getState().addSeat(seat));

      expect(useSeatSelectionStore.getState().selectedSeats).toHaveLength(4);
      expect(useSeatSelectionStore.getState().selectedSeats.map(s => s.id)).not.toContain('seat-5');
    });
  });

  describe('removeSeat', () => {
    it('선택된 좌석을 제거할 수 있다', () => {
      const seat1 = createMockSeat('seat-1', 1, 1);
      const seat2 = createMockSeat('seat-2', 1, 2);

      useSeatSelectionStore.getState().addSeat(seat1);
      useSeatSelectionStore.getState().addSeat(seat2);
      useSeatSelectionStore.getState().removeSeat('seat-1');

      expect(useSeatSelectionStore.getState().selectedSeats).toHaveLength(1);
      expect(useSeatSelectionStore.getState().selectedSeats[0].id).toBe('seat-2');
    });

    it('존재하지 않는 좌석 제거 시 에러가 발생하지 않는다', () => {
      expect(() => {
        useSeatSelectionStore.getState().removeSeat('non-existent');
      }).not.toThrow();
    });
  });

  describe('clearSeats', () => {
    it('모든 선택된 좌석을 초기화할 수 있다', () => {
      const seats = [
        createMockSeat('seat-1', 1, 1),
        createMockSeat('seat-2', 1, 2),
        createMockSeat('seat-3', 1, 3),
      ];

      seats.forEach((seat) => useSeatSelectionStore.getState().addSeat(seat));
      expect(useSeatSelectionStore.getState().selectedSeats).toHaveLength(3);

      useSeatSelectionStore.getState().clearSeats();
      expect(useSeatSelectionStore.getState().selectedSeats).toHaveLength(0);
    });
  });

  describe('isSeatSelected', () => {
    it('좌석이 선택되었는지 확인할 수 있다', () => {
      const seat = createMockSeat('seat-1', 1, 1);

      expect(useSeatSelectionStore.getState().isSeatSelected('seat-1')).toBe(false);

      useSeatSelectionStore.getState().addSeat(seat);
      expect(useSeatSelectionStore.getState().isSeatSelected('seat-1')).toBe(true);
    });
  });

  describe('canSelectMore', () => {
    it('4석 미만일 때 true를 반환한다', () => {
      expect(useSeatSelectionStore.getState().canSelectMore()).toBe(true);

      useSeatSelectionStore.getState().addSeat(createMockSeat('seat-1', 1, 1));
      expect(useSeatSelectionStore.getState().canSelectMore()).toBe(true);

      useSeatSelectionStore.getState().addSeat(createMockSeat('seat-2', 1, 2));
      expect(useSeatSelectionStore.getState().canSelectMore()).toBe(true);

      useSeatSelectionStore.getState().addSeat(createMockSeat('seat-3', 1, 3));
      expect(useSeatSelectionStore.getState().canSelectMore()).toBe(true);
    });

    it('4석일 때 false를 반환한다', () => {
      const seats = [
        createMockSeat('seat-1', 1, 1),
        createMockSeat('seat-2', 1, 2),
        createMockSeat('seat-3', 1, 3),
        createMockSeat('seat-4', 1, 4),
      ];

      seats.forEach((seat) => useSeatSelectionStore.getState().addSeat(seat));
      expect(useSeatSelectionStore.getState().canSelectMore()).toBe(false);
    });
  });
});
