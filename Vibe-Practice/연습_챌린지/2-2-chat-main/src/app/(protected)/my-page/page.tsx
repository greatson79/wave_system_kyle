'use client';

import React from 'react';
import { MyPageHeader } from '@/features/users/components/my-page-header';
import { UserInfoSection } from '@/features/users/components/user-info-section';
import { NicknameForm } from '@/features/users/components/nickname-form';
import { LogoutButton } from '@/features/users/components/logout-button';
import { LoadingSpinner } from '@/components/common/loading-spinner';
import { ErrorMessage } from '@/components/common/error-message';
import { useUserProfile } from '@/features/users/hooks/use-user-profile';

export default function MyPage() {
  const { data: userProfile, isLoading, error, refetch } = useUserProfile();

  return (
    <div className="flex flex-col h-screen">
      <MyPageHeader />
      {isLoading && <LoadingSpinner />}
      {error && (
        <ErrorMessage
          message="프로필을 불러오는 데 실패했습니다"
          onRetry={() => refetch()}
        />
      )}
      {userProfile && (
        <>
          <div className="flex-1 overflow-y-auto">
            <UserInfoSection userProfile={userProfile} />
            <NicknameForm userProfile={userProfile} />
          </div>
          <LogoutButton />
        </>
      )}
    </div>
  );
}
