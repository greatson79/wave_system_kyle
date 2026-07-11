import * as React from "react";
import { Slot } from "@radix-ui/react-slot";
import { cva, type VariantProps } from "class-variance-authority";

import { cn } from "@/lib/utils";

const buttonVariants = cva(
  "inline-flex items-center justify-center whitespace-nowrap rounded-lg text-sm font-semibold transition-all duration-200 focus-visible:outline-hidden focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50",
  {
    variants: {
      variant: {
        default: "bg-primary text-white hover:bg-primary/90 shadow-md hover:shadow-lg",
        primary: "bg-[hsl(270,60%,50%)] text-white hover:bg-[hsl(270,70%,40%)] shadow-lg hover:shadow-xl hover:scale-105",
        secondary:
          "border-2 border-primary text-primary bg-transparent hover:bg-primary hover:text-white shadow-md hover:shadow-lg",
        destructive:
          "bg-[hsl(350,85%,60%)] text-white hover:bg-[hsl(350,85%,50%)] shadow-md hover:shadow-lg",
        outline:
          "border-2 border-[hsl(270,12%,88%)] bg-background hover:bg-[hsl(270,20%,98%)] hover:text-[hsl(270,15%,15%)]",
        ghost: "text-primary hover:bg-primary/10 hover:text-primary",
        link: "text-[hsl(240,60%,60%)] underline-offset-4 hover:underline",
      },
      size: {
        default: "h-11 px-6 py-3",
        sm: "h-9 rounded-lg px-4 py-2",
        lg: "h-12 rounded-lg px-8 py-3",
        icon: "h-10 w-10",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  },
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : "button";
    return (
      <Comp
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        {...props}
      />
    );
  },
);
Button.displayName = "Button";

export { Button, buttonVariants };
