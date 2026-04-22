'use client';

import { create } from 'zustand';
import type { Seat } from '../backend/schema';

interface SeatSelectionState {
  selectedSeats: Seat[];
  addSeat: (seat: Seat) => void;
  removeSeat: (seatId: string) => void;
  clearSeats: () => void;
  isSeatSelected: (seatId: string) => boolean;
  canSelectMore: () => boolean;
}

export const useSeatSelectionStore = create<SeatSelectionState>((set, get) => ({
  selectedSeats: [],

  addSeat: (seat: Seat) => {
    const current = get().selectedSeats;

    if (current.some((s) => s.id === seat.id)) {
      return;
    }

    if (current.length >= 4) {
      return;
    }

    set({ selectedSeats: [...current, seat] });
  },

  removeSeat: (seatId: string) => {
    set((state) => ({
      selectedSeats: state.selectedSeats.filter((s) => s.id !== seatId),
    }));
  },

  clearSeats: () => {
    set({ selectedSeats: [] });
  },

  isSeatSelected: (seatId: string) => {
    return get().selectedSeats.some((s) => s.id === seatId);
  },

  canSelectMore: () => {
    return get().selectedSeats.length < 4;
  },
}));
