import * as React from "react";
import { cva, type VariantProps } from "class-variance-authority";

import { cn } from "@/lib/utils";

const badgeVariants = cva(
  "inline-flex items-center rounded-full border px-3 py-1 text-xs font-semibold transition-all duration-200 focus:outline-hidden focus:ring-2 focus:ring-ring focus:ring-offset-2",
  {
    variants: {
      variant: {
        default:
          "border-transparent bg-primary text-white hover:bg-primary/80 shadow-sm",
        primary:
          "border-transparent bg-[hsl(270,60%,50%)] text-white hover:bg-[hsl(270,70%,40%)] shadow-sm",
        secondary:
          "border-transparent bg-[hsl(300,60%,60%)] text-white hover:bg-[hsl(300,60%,50%)] shadow-sm",
        success:
          "border-transparent bg-[hsl(150,60%,45%)] text-white hover:bg-[hsl(150,60%,40%)] shadow-sm",
        warning:
          "border-transparent bg-[hsl(40,95%,55%)] text-white hover:bg-[hsl(40,95%,50%)] shadow-sm",
        destructive:
          "border-transparent bg-[hsl(350,85%,60%)] text-white hover:bg-[hsl(350,85%,50%)] shadow-sm",
        outline: "border-primary text-primary hover:bg-primary/10",
        gradient:
          "border-transparent bg-gradient-to-r from-[hsl(270,60%,50%)] to-[hsl(300,60%,60%)] text-white hover:opacity-90 shadow-md",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  },
);

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return (
    <div className={cn(badgeVariants({ variant }), className)} {...props} />
  );
}

export { Badge, badgeVariants };
