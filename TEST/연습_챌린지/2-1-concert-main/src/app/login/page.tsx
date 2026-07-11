"use client";

import { useCallback, useEffect, useState } from "react";
import Image from "next/image";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { Music } from "lucide-react";
import { getSupabaseBrowserClient } from "@/lib/supabase/browser-client";
import { useCurrentUser } from "@/features/auth/hooks/useCurrentUser";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

type LoginPageProps = {
  params: Promise<Record<string, never>>;
};

export default function LoginPage({ params }: LoginPageProps) {
  void params;
  const router = useRouter();
  const searchParams = useSearchParams();
  const { refresh, isAuthenticated } = useCurrentUser();
  const [formState, setFormState] = useState({ email: "", password: "" });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  useEffect(() => {
    if (isAuthenticated) {
      const redirectedFrom = searchParams.get("redirectedFrom") ?? "/";
      router.replace(redirectedFrom);
    }
  }, [isAuthenticated, router, searchParams]);

  const handleChange = useCallback(
    (event: React.ChangeEvent<HTMLInputElement>) => {
      const { name, value } = event.target;
      setFormState((prev) => ({ ...prev, [name]: value }));
    },
    []
  );

  const handleSubmit = useCallback(
    async (event: React.FormEvent<HTMLFormElement>) => {
      event.preventDefault();
      setIsSubmitting(true);
      setErrorMessage(null);
      const supabase = getSupabaseBrowserClient();

      try {
        const result = await supabase.auth.signInWithPassword({
          email: formState.email,
          password: formState.password,
        });

        const nextAction = result.error
          ? result.error.message ?? "로그인에 실패했습니다."
          : ("success" as const);

        if (nextAction === "success") {
          await refresh();
          const redirectedFrom = searchParams.get("redirectedFrom") ?? "/";
          router.replace(redirectedFrom);
        } else {
          setErrorMessage(nextAction);
        }
      } catch (error) {
        setErrorMessage("로그인 처리 중 오류가 발생했습니다.");
      } finally {
        setIsSubmitting(false);
      }
    },
    [formState.email, formState.password, refresh, router, searchParams]
  );

  if (isAuthenticated) {
    return null;
  }

  return (
    <div className="min-h-screen flex items-center justify-center py-16 px-6">
      <div className="w-full max-w-md mx-auto">
        <div className="border border-[hsl(270,12%,88%)] shadow-xl rounded-xl p-8 bg-white">
          {/* Logo & Branding */}
          <div className="flex items-center justify-center gap-2 mb-2">
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-[hsl(270,60%,50%)] to-[hsl(300,60%,60%)] flex items-center justify-center">
              <Music className="w-5 h-5 text-white" />
            </div>
            <span className="text-2xl font-bold bg-gradient-to-r from-[hsl(270,60%,50%)] to-[hsl(300,60%,60%)] bg-clip-text text-transparent">
              SuperNext
            </span>
          </div>

          {/* Title */}
          <h1 className="text-3xl font-bold text-center mb-2 text-[hsl(270,15%,15%)]">
            로그인
          </h1>
          <p className="text-center text-[hsl(270,8%,50%)] mb-8">
            계정으로 로그인하고 콘서트를 예매하세요
          </p>

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="email" className="text-sm font-semibold text-[hsl(270,10%,30%)]">
                이메일
              </Label>
              <Input
                id="email"
                type="email"
                name="email"
                autoComplete="email"
                required
                value={formState.email}
                onChange={handleChange}
                placeholder="your@email.com"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="password" className="text-sm font-semibold text-[hsl(270,10%,30%)]">
                비밀번호
              </Label>
              <Input
                id="password"
                type="password"
                name="password"
                autoComplete="current-password"
                required
                value={formState.password}
                onChange={handleChange}
                placeholder="••••••••"
              />
            </div>

            {errorMessage && (
              <div className="rounded-lg bg-[hsl(350,85%,60%)]/10 border border-[hsl(350,85%,60%)]/20 p-3">
                <p className="text-sm text-[hsl(350,85%,50%)]">{errorMessage}</p>
              </div>
            )}

            <Button
              type="submit"
              disabled={isSubmitting}
              variant="primary"
              className="w-full"
              size="lg"
            >
              {isSubmitting ? "로그인 중..." : "로그인"}
            </Button>

            <p className="text-center text-sm text-[hsl(270,8%,50%)]">
              계정이 없으신가요?{" "}
              <Link
                href="/signup"
                className="text-[hsl(270,60%,50%)] hover:underline font-semibold transition-colors duration-200 underline-offset-4"
              >
                회원가입
              </Link>
            </p>
          </form>
        </div>
      </div>
    </div>
  );
}
