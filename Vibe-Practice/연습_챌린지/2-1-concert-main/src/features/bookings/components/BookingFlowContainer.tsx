'use client';

import { useState } from 'react';
import { SeatSelectionStep } from './SeatSelectionStep';
import { BookingFormStep } from './BookingFormStep';
import { useSeatSelectionStore } from '../stores/useSeatSelectionStore';

interface BookingFlowContainerProps {
  concertId: string;
}

type FlowStep = 'seat-selection' | 'booking-form';

export const BookingFlowContainer = ({ concertId }: BookingFlowContainerProps) => {
  const [currentStep, setCurrentStep] = useState<FlowStep>('seat-selection');
  const { selectedSeats } = useSeatSelectionStore();

  const handleProceedToForm = () => {
    if (selectedSeats.length > 0) {
      setCurrentStep('booking-form');
    }
  };

  const handleBackToSeatSelection = () => {
    setCurrentStep('seat-selection');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {currentStep === 'seat-selection' && (
        <SeatSelectionStep concertId={concertId} onProceed={handleProceedToForm} />
      )}

      {currentStep === 'booking-form' && (
        <BookingFormStep concertId={concertId} onBack={handleBackToSeatSelection} />
      )}
    </div>
  );
};
