"use client";

import Link from "next/link";
import { useState } from "react";
import { Menu, X, Music } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function Header() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const toggleMobileMenu = () => {
    setMobileMenuOpen(!mobileMenuOpen);
  };

  return (
    <header className="sticky top-0 z-50 h-16 border-b border-gray-200 bg-white/80 shadow-sm backdrop-blur-md">
      <div className="mx-auto flex h-full max-w-7xl items-center justify-between px-6 md:px-8 lg:px-12">
        {/* 로고 영역 */}
        <Link
          href="/"
          className="flex items-center gap-2 text-xl font-bold text-primary transition-colors duration-200 hover:text-primary-dark"
        >
          <Music className="h-6 w-6" />
          <span>SuperNext</span>
        </Link>

        {/* 데스크탑 네비게이션 */}
        <nav className="hidden items-center gap-8 md:flex">
          <Link
            href="/"
            className="font-semibold text-gray-700 underline-offset-4 transition-colors duration-200 hover:text-primary hover:underline"
          >
            콘서트
          </Link>
          <Link
            href="/bookings/lookup"
            className="font-semibold text-gray-700 underline-offset-4 transition-colors duration-200 hover:text-primary hover:underline"
          >
            예약 조회
          </Link>
        </nav>
      </div>
    </header>
  );
}
