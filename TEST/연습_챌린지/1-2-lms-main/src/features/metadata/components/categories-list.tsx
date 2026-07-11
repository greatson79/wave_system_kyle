'use client';

import { useState } from 'react';
import { format } from 'date-fns';
import { ko } from 'date-fns/locale';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Skeleton } from '@/components/ui/skeleton';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';
import { useCategories } from '../hooks/useCategories';
import { useUpdateCategory } from '../hooks/useUpdateCategory';
import { CategoryFormDialog } from './category-form-dialog';
import type { CategoryItem } from '../lib/dto';

export function CategoriesList() {
  const { data, isLoading, error } = useCategories();
  const { mutate: updateCategory } = useUpdateCategory();
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [editingCategory, setEditingCategory] = useState<CategoryItem | null>(
    null
  );
  const [deactivatingCategory, setDeactivatingCategory] =
    useState<CategoryItem | null>(null);

  const handleEdit = (category: CategoryItem) => {
    setEditingCategory(category);
  };

  const handleDeactivate = (category: CategoryItem) => {
    setDeactivatingCategory(category);
  };

  const handleConfirmDeactivate = () => {
    if (deactivatingCategory) {
      updateCategory(
        {
          categoryId: deactivatingCategory.id,
          data: { isActive: false },
        },
        {
          onSuccess: () => {
            setDeactivatingCategory(null);
          },
        }
      );
    }
  };

  const handleActivate = (categoryId: string) => {
    updateCategory({
      categoryId,
      data: { isActive: true },
    });
  };

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertDescription>{error.message}</AlertDescription>
      </Alert>
    );
  }

  return (
    <>
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle>카테고리 관리</CardTitle>
            <Button onClick={() => setIsCreateDialogOpen(true)}>
              새 카테고리 추가
            </Button>
          </div>
        </CardHeader>

        <CardContent>
          {isLoading ? (
            <div className="space-y-2">
              <Skeleton className="h-12 w-full" />
              <Skeleton className="h-12 w-full" />
              <Skeleton className="h-12 w-full" />
            </div>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>이름</TableHead>
                  <TableHead>상태</TableHead>
                  <TableHead>생성일</TableHead>
                  <TableHead>수정일</TableHead>
                  <TableHead className="text-right">작업</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {data?.categories.length === 0 ? (
                  <TableRow>
                    <TableCell
                      colSpan={5}
                      className="text-center text-muted-foreground"
                    >
                      등록된 카테고리가 없습니다.
                    </TableCell>
                  </TableRow>
                ) : (
                  data?.categories.map((category) => (
                    <TableRow key={category.id}>
                      <TableCell className="font-medium">
                        {category.name}
                      </TableCell>
                      <TableCell>
                        <Badge
                          variant={category.isActive ? 'default' : 'secondary'}
                        >
                          {category.isActive ? '활성' : '비활성'}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        {format(new Date(category.createdAt), 'PPP', {
                          locale: ko,
                        })}
                      </TableCell>
                      <TableCell>
                        {format(new Date(category.updatedAt), 'PPP', {
                          locale: ko,
                        })}
                      </TableCell>
                      <TableCell className="text-right space-x-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleEdit(category)}
                        >
                          수정
                        </Button>
                        {category.isActive ? (
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleDeactivate(category)}
                          >
                            비활성화
                          </Button>
                        ) : (
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleActivate(category.id)}
                          >
                            활성화
                          </Button>
                        )}
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>

      <CategoryFormDialog
        open={isCreateDialogOpen}
        onOpenChange={setIsCreateDialogOpen}
      />

      {editingCategory && (
        <CategoryFormDialog
          open={!!editingCategory}
          onOpenChange={(open) => !open && setEditingCategory(null)}
          category={editingCategory}
        />
      )}

      <AlertDialog
        open={!!deactivatingCategory}
        onOpenChange={(open) => !open && setDeactivatingCategory(null)}
      >
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>카테고리 비활성화</AlertDialogTitle>
            <AlertDialogDescription>
              &quot;{deactivatingCategory?.name}&quot; 카테고리를
              비활성화하시겠습니까? 비활성화된 카테고리는 새 코스 생성 시 선택할
              수 없습니다. 기존에 이 카테고리를 사용하는 코스는 계속 표시됩니다.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>취소</AlertDialogCancel>
            <AlertDialogAction onClick={handleConfirmDeactivate}>
              비활성화
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </>
  );
}
