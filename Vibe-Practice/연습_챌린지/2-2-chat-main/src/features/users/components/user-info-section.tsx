'use client';

import React from 'react';
import type { UserProfile } from '../types';

export type UserInfoSectionProps = {
  userProfile: UserProfile;
};

export const UserInfoSection: React.FC<UserInfoSectionProps> = ({
  userProfile,
}) => {
  return (
    <div className="p-6 space-y-4">
      <div>
        <label className="text-sm text-muted-foreground">이메일</label>
        <p className="text-base text-foreground">{userProfile.email}</p>
      </div>
      <div>
        <label className="text-sm text-muted-foreground">닉네임</label>
        <p className="text-base text-foreground">{userProfile.nickname}</p>
      </div>
    </div>
  );
};
