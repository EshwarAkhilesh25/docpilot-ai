import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useNavigate } from "react-router-dom";
import { toast } from "sonner";
import { motion } from "framer-motion";
import { authService } from "@services/authService";
import { registerSchema, RegisterInput } from "@lib/validations/auth";
import { ROUTES } from "@lib/constants";
import { pageTransition, cardVariants } from "@lib/animations";
import { AuthLayout } from "@components/layout/AuthLayout";
import { AuthCard } from "@components/auth/AuthCard";
import { AuthHeader } from "@components/auth/AuthHeader";
import { AuthFooter } from "@components/auth/AuthFooter";
import { PasswordInput } from "@components/auth/PasswordInput";
import { FormField } from "@components/auth/FormField";
import { Button } from "@components/common/Button";
import { PremiumBackground } from "@components/common/PremiumBackground";

export default function Register() {
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);
  const [globalError, setGlobalError] = useState<string | null>(null);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterInput>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      full_name: "",
      email: "",
      password: "",
      confirmPassword: "",
    },
  });

  const onSubmit = async (data: RegisterInput) => {
    setIsLoading(true);
    setGlobalError(null);

    try {
      await authService.register(data);
      toast.success("Account created successfully! Please sign in.");
      navigate(ROUTES.LOGIN);
    } catch (err: unknown) {
      const error = err as Error & {
        response?: { data?: { detail?: string }; status?: number };
      };
      if (error.response?.status === 409) {
        setGlobalError("Email already registered");
      } else if (error.response?.status === 400) {
        setGlobalError("Invalid input data");
      } else if (error.response?.status === 422) {
        setGlobalError("Invalid input data");
      } else if (error.response?.status === 500) {
        setGlobalError("Server error. Please try again later.");
      } else {
        setGlobalError("An error occurred. Please try again.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <AuthLayout>
      <PremiumBackground variant="gradient" />
      <motion.div
        variants={pageTransition}
        initial="initial"
        animate="animate"
        exit="exit"
        className="w-full"
      >
        <AuthCard className="p-10">
          <motion.div
            variants={cardVariants}
            initial="initial"
            animate="animate"
          >
            <AuthHeader
              title="Create Account"
              description="Sign up to get started with DocMind AI"
            />

            {globalError && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="mb-6 p-4 bg-destructive/10 border border-destructive/20 rounded-lg"
                role="alert"
              >
                <p className="text-sm text-destructive">{globalError}</p>
              </motion.div>
            )}

            <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
              <FormField
                label="Full Name"
                error={errors.full_name?.message}
                required
              >
                <input
                  type="text"
                  autoComplete="name"
                  autoFocus
                  disabled={isLoading}
                  className="flex h-12 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 transition-all duration-200"
                  {...register("full_name")}
                />
              </FormField>

              <FormField label="Email" error={errors.email?.message} required>
                <input
                  type="email"
                  autoComplete="email"
                  disabled={isLoading}
                  className="flex h-12 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 transition-all duration-200"
                  {...register("email")}
                />
              </FormField>

              <FormField
                label="Password"
                error={errors.password?.message}
                required
              >
                <PasswordInput
                  autoComplete="new-password"
                  disabled={isLoading}
                  {...register("password")}
                />
              </FormField>

              <FormField
                label="Confirm Password"
                error={errors.confirmPassword?.message}
                required
              >
                <PasswordInput
                  autoComplete="new-password"
                  disabled={isLoading}
                  {...register("confirmPassword")}
                />
              </FormField>

              <Button
                type="submit"
                className="w-full"
                loading={isLoading}
                disabled={isLoading}
              >
                {isLoading ? "Creating account..." : "Create Account"}
              </Button>
            </form>

            <AuthFooter>
              <span className="text-muted-foreground">
                Already have an account?{" "}
              </span>
              <a
                href={ROUTES.LOGIN}
                className="text-primary hover:underline font-medium"
              >
                Sign in
              </a>
            </AuthFooter>
          </motion.div>
        </AuthCard>
      </motion.div>
    </AuthLayout>
  );
}
