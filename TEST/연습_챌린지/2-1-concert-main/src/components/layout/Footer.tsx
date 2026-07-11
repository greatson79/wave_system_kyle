'use client';

import Link from 'next/link';
import { Music, Mail, Phone, MapPin } from 'lucide-react';

export default function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="border-t border-gray-200 bg-gradient-to-b from-white to-purple-50">
      <div className="mx-auto max-w-7xl px-6 py-12 md:px-8 md:py-16 lg:px-12">
        {/* 상단 영역 */}
        <div className="grid grid-cols-1 gap-8 md:grid-cols-2 lg:grid-cols-4">
          {/* 회사 정보 */}
          <div className="space-y-4">
            <Link
              href="/"
              className="flex items-center gap-2 text-xl font-bold text-primary transition-colors duration-200 hover:text-primary-dark"
            >
              <Music className="h-6 w-6" />
              <span>SuperNext</span>
            </Link>
            <p className="text-sm leading-relaxed text-gray-500">
              최고의 콘서트 예매 경험을 제공하는 플랫폼입니다.
              편리하고 빠른 예약으로 잊지 못할 순간을 만들어보세요.
            </p>
            <div className="flex gap-4">
              <a
                href="mailto:info@supernext.com"
                className="rounded-lg p-2 text-gray-500 transition-colors duration-200 hover:bg-primary/10 hover:text-primary"
                aria-label="이메일"
              >
                <Mail className="h-5 w-5" />
              </a>
              <a
                href="tel:+821234567890"
                className="rounded-lg p-2 text-gray-500 transition-colors duration-200 hover:bg-primary/10 hover:text-primary"
                aria-label="전화"
              >
                <Phone className="h-5 w-5" />
              </a>
            </div>
          </div>

          {/* 콘서트 링크 */}
          <div className="space-y-4">
            <h3 className="text-sm font-semibold text-gray-900">콘서트</h3>
            <ul className="space-y-2">
              <li>
                <Link
                  href="/concerts"
                  className="text-sm text-gray-500 underline-offset-4 transition-colors duration-200 hover:text-primary hover:underline"
                >
                  전체 콘서트
                </Link>
              </li>
              <li>
                <Link
                  href="/concerts?category=upcoming"
                  className="text-sm text-gray-500 underline-offset-4 transition-colors duration-200 hover:text-primary hover:underline"
                >
                  예정 공연
                </Link>
              </li>
              <li>
                <Link
                  href="/concerts?category=popular"
                  className="text-sm text-gray-500 underline-offset-4 transition-colors duration-200 hover:text-primary hover:underline"
                >
                  인기 공연
                </Link>
              </li>
            </ul>
          </div>

          {/* 예약 조회 링크 */}
          <div className="space-y-4">
            <h3 className="text-sm font-semibold text-gray-900">예약 관리</h3>
            <ul className="space-y-2">
              <li>
                <Link
                  href="/reservations"
                  className="text-sm text-gray-500 underline-offset-4 transition-colors duration-200 hover:text-primary hover:underline"
                >
                  예약 조회
                </Link>
              </li>
              <li>
                <Link
                  href="/reservations/my"
                  className="text-sm text-gray-500 underline-offset-4 transition-colors duration-200 hover:text-primary hover:underline"
                >
                  내 예약
                </Link>
              </li>
              <li>
                <Link
                  href="/reservations/cancel"
                  className="text-sm text-gray-500 underline-offset-4 transition-colors duration-200 hover:text-primary hover:underline"
                >
                  예약 취소
                </Link>
              </li>
            </ul>
          </div>

          {/* 고객센터 링크 */}
          <div className="space-y-4">
            <h3 className="text-sm font-semibold text-gray-900">고객센터</h3>
            <ul className="space-y-2">
              <li>
                <Link
                  href="/help/faq"
                  className="text-sm text-gray-500 underline-offset-4 transition-colors duration-200 hover:text-primary hover:underline"
                >
                  자주 묻는 질문
                </Link>
              </li>
              <li>
                <Link
                  href="/help/contact"
                  className="text-sm text-gray-500 underline-offset-4 transition-colors duration-200 hover:text-primary hover:underline"
                >
                  문의하기
                </Link>
              </li>
              <li>
                <Link
                  href="/help/terms"
                  className="text-sm text-gray-500 underline-offset-4 transition-colors duration-200 hover:text-primary hover:underline"
                >
                  이용약관
                </Link>
              </li>
              <li>
                <Link
                  href="/help/privacy"
                  className="text-sm text-gray-500 underline-offset-4 transition-colors duration-200 hover:text-primary hover:underline"
                >
                  개인정보처리방침
                </Link>
              </li>
            </ul>
          </div>
        </div>

        {/* 하단 영역 */}
        <div className="mt-12 border-t border-gray-200 pt-8">
          <div className="flex flex-col items-center gap-4 md:flex-row md:justify-between">
            {/* 저작권 */}
            <p className="text-xs text-gray-500">
              &copy; {currentYear} SuperNext. All rights reserved.
            </p>

            {/* 주소 정보 */}
            <div className="flex items-center gap-2 text-xs text-gray-500">
              <MapPin className="h-4 w-4" />
              <span>서울특별시 강남구 테헤란로 123, 7층</span>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}
