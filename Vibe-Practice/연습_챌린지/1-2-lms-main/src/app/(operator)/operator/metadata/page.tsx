'use client';

import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { CategoriesList } from '@/features/metadata/components/categories-list';
import { DifficultiesList } from '@/features/metadata/components/difficulties-list';

export default function MetadataManagementPage() {
  return (
    <div className="container mx-auto py-8">
      <div className="mb-6">
        <h1 className="text-3xl font-bold">메타데이터 관리</h1>
        <p className="text-muted-foreground mt-2">
          코스 카테고리와 난이도를 관리할 수 있습니다.
        </p>
      </div>

      <Tabs defaultValue="categories" className="space-y-6">
        <TabsList>
          <TabsTrigger value="categories">카테고리</TabsTrigger>
          <TabsTrigger value="difficulties">난이도</TabsTrigger>
        </TabsList>

        <TabsContent value="categories" className="space-y-6">
          <CategoriesList />
        </TabsContent>

        <TabsContent value="difficulties" className="space-y-6">
          <DifficultiesList />
        </TabsContent>
      </Tabs>
    </div>
  );
}
