'use client';

import { useState } from 'react';
import { BookingLookupForm } from './BookingLookupForm';
import { BookingListDisplay } from './BookingListDisplay';
import type { LookupBookingsResponse } from '../lib/dto';

export const BookingLookupContainer = () => {
  const [lookupResult, setLookupResult] = useState<LookupBookingsResponse | null>(null);
  const [credentials, setCredentials] = useState<{ phone: string; password: string } | null>(null);

  const handleLookupSuccess = (result: LookupBookingsResponse, phone: string, password: string) => {
    setLookupResult(result);
    setCredentials({ phone, password });
  };

  const handleBackToForm = () => {
    setLookupResult(null);
    setCredentials(null);
  };

  return (
    <div className="max-w-4xl mx-auto">
      {!lookupResult && <BookingLookupForm onSuccess={handleLookupSuccess} />}

      {lookupResult && credentials && (
        <BookingListDisplay
          bookings={lookupResult.bookings}
          phone={credentials.phone}
          password={credentials.password}
          onBack={handleBackToForm}
        />
      )}
    </div>
  );
};
