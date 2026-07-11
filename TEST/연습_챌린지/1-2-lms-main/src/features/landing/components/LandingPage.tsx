'use client'

import Link from 'next/link'
import { Button } from '@/components/ui/button'
import { BookOpen, ClipboardList, Award } from 'lucide-react'

export default function LandingPage() {
  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="bg-gradient-to-b from-blue-50 to-white py-20">
        <div className="container mx-auto px-4 text-center">
          <h1 className="text-5xl font-bold text-gray-900 mb-6">
            온라인 학습의 새로운 기준
          </h1>
          <p className="text-xl text-gray-600 mb-8 max-w-2xl mx-auto">
            강사와 학습자를 연결하는 통합 LMS 플랫폼.
            코스 수강부터 과제 제출, 채점까지 한 곳에서.
          </p>
          <div className="flex gap-4 justify-center">
            <Button asChild size="lg">
              <Link href="/signup">시작하기</Link>
            </Button>
            <Button asChild variant="outline" size="lg">
              <Link href="/login">로그인</Link>
            </Button>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl font-bold text-center mb-12">
            주요 기능
          </h2>
          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center p-6">
              <BookOpen className="w-12 h-12 mx-auto mb-4 text-blue-600" />
              <h3 className="text-xl font-semibold mb-2">다양한 코스</h3>
              <p className="text-gray-600">
                카테고리와 난이도별로 분류된 풍부한 코스 카탈로그
              </p>
            </div>

            <div className="text-center p-6">
              <ClipboardList className="w-12 h-12 mx-auto mb-4 text-green-600" />
              <h3 className="text-xl font-semibold mb-2">과제 관리</h3>
              <p className="text-gray-600">
                과제 제출부터 재제출까지 체계적인 과제 관리 시스템
              </p>
            </div>

            <div className="text-center p-6">
              <Award className="w-12 h-12 mx-auto mb-4 text-purple-600" />
              <h3 className="text-xl font-semibold mb-2">실시간 피드백</h3>
              <p className="text-gray-600">
                강사의 상세한 채점 및 피드백으로 빠른 성장 지원
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-blue-600 text-white py-16">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold mb-4">지금 바로 시작하세요</h2>
          <p className="text-xl mb-8">학습자든 강사든, 누구나 환영합니다</p>
          <Button asChild size="lg" variant="secondary">
            <Link href="/signup">무료로 가입하기</Link>
          </Button>
        </div>
      </section>
    </div>
  )
}
