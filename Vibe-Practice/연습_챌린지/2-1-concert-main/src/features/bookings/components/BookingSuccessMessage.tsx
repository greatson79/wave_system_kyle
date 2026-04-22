'use client';

import { CheckCircle } from 'lucide-react';

export const BookingSuccessMessage = () => {
  return (
    <div className="bg-white rounded-lg p-8 shadow-sm text-center">
      <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-green-100 mb-4">
        <CheckCircle className="w-10 h-10 text-green-600" />
      </div>
      <h1 className="text-3xl font-bold text-gray-900 mb-2">예약이 완료되었습니다!</h1>
      <p className="text-gray-600">
        예약 정보를 확인해주세요.
        <br />
        휴대폰번호와 비밀번호로 언제든지 조회하실 수 있습니다.
      </p>
    </div>
  );
};
