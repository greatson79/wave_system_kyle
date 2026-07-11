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
import { useDifficulties } from '../hooks/useDifficulties';
import { useUpdateDifficulty } from '../hooks/useUpdateDifficulty';
import { DifficultyFormDialog } from './difficulty-form-dialog';
import type { DifficultyItem } from '../lib/dto';

export function DifficultiesList() {
  const { data, isLoading, error } = useDifficulties();
  const { mutate: updateDifficulty } = useUpdateDifficulty();
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [editingDifficulty, setEditingDifficulty] =
    useState<DifficultyItem | null>(null);
  const [deactivatingDifficulty, setDeactivatingDifficulty] =
    useState<DifficultyItem | null>(null);

  const handleEdit = (difficulty: DifficultyItem) => {
    setEditingDifficulty(difficulty);
  };

  const handleDeactivate = (difficulty: DifficultyItem) => {
    setDeactivatingDifficulty(difficulty);
  };

  const handleConfirmDeactivate = () => {
    if (deactivatingDifficulty) {
      updateDifficulty(
        {
          difficultyId: deactivatingDifficulty.id,
          data: { isActive: false },
        },
        {
          onSuccess: () => {
            setDeactivatingDifficulty(null);
          },
        }
      );
    }
  };

  const handleActivate = (difficultyId: string) => {
    updateDifficulty({
      difficultyId,
      data: { isActive: true },
    });
  };

  const sortedDifficulties = data?.difficulties.sort((a, b) => a.level - b.level);

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
            <CardTitle>난이도 관리</CardTitle>
            <Button onClick={() => setIsCreateDialogOpen(true)}>
              새 난이도 추가
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
                  <TableHead>레벨</TableHead>
                  <TableHead>상태</TableHead>
                  <TableHead>생성일</TableHead>
                  <TableHead>수정일</TableHead>
                  <TableHead className="text-right">작업</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {sortedDifficulties?.length === 0 ? (
                  <TableRow>
                    <TableCell
                      colSpan={6}
                      className="text-center text-muted-foreground"
                    >
                      등록된 난이도가 없습니다.
                    </TableCell>
                  </TableRow>
                ) : (
                  sortedDifficulties?.map((difficulty) => (
                    <TableRow key={difficulty.id}>
                      <TableCell className="font-medium">
                        {difficulty.name}
                      </TableCell>
                      <TableCell>
                        <Badge variant="outline">Level {difficulty.level}</Badge>
                      </TableCell>
                      <TableCell>
                        <Badge
                          variant={difficulty.isActive ? 'default' : 'secondary'}
                        >
                          {difficulty.isActive ? '활성' : '비활성'}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        {format(new Date(difficulty.createdAt), 'PPP', {
                          locale: ko,
                        })}
                      </TableCell>
                      <TableCell>
                        {format(new Date(difficulty.updatedAt), 'PPP', {
                          locale: ko,
                        })}
                      </TableCell>
                      <TableCell className="text-right space-x-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleEdit(difficulty)}
                        >
                          수정
                        </Button>
                        {difficulty.isActive ? (
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleDeactivate(difficulty)}
                          >
                            비활성화
                          </Button>
                        ) : (
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleActivate(difficulty.id)}
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

      <DifficultyFormDialog
        open={isCreateDialogOpen}
        onOpenChange={setIsCreateDialogOpen}
      />

      {editingDifficulty && (
        <DifficultyFormDialog
          open={!!editingDifficulty}
          onOpenChange={(open) => !open && setEditingDifficulty(null)}
          difficulty={editingDifficulty}
        />
      )}

      <AlertDialog
        open={!!deactivatingDifficulty}
        onOpenChange={(open) => !open && setDeactivatingDifficulty(null)}
      >
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>난이도 비활성화</AlertDialogTitle>
            <AlertDialogDescription>
              &quot;{deactivatingDifficulty?.name}&quot; 난이도를
              비활성화하시겠습니까? 비활성화된 난이도는 새 코스 생성 시 선택할 수
              없습니다. 기존에 이 난이도를 사용하는 코스는 계속 표시됩니다.
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
