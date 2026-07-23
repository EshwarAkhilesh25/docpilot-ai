import { useState, useEffect, useCallback, useRef } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Check, X } from "lucide-react";
import {
  changePasswordSchema,
  ChangePasswordInput,
} from "@lib/validations/settings";
import { useChangePassword } from "@hooks/useSettings";
import { Button } from "@components/common/Button";
import { FormField } from "@components/auth/FormField";
import { PasswordInput } from "@components/auth/PasswordInput";

export function ChangePasswordForm() {
  const [isSuccess, setIsSuccess] = useState(false);
  const changePassword = useChangePassword();
  const currentPasswordRef = useRef<HTMLInputElement>(null);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting, isDirty },
  } = useForm<ChangePasswordInput>({
    resolver: zodResolver(changePasswordSchema),
    defaultValues: {
      current_password: "",
      new_password: "",
      confirm_password: "",
    },
  });

  // Handle escape key to cancel
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === "Escape" && !isSubmitting) {
        reset();
      }
    };
    window.addEventListener("keydown", handleEscape);
    return () => window.removeEventListener("keydown", handleEscape);
  }, [reset, isSubmitting]);

  const onSubmit = useCallback(
    async (data: ChangePasswordInput) => {
      try {
        await changePassword.mutateAsync(data);
        setIsSuccess(true);
        reset();
        // Focus first field after successful update
        setTimeout(() => {
          currentPasswordRef.current?.focus();
        }, 100);
        setTimeout(() => setIsSuccess(false), 3000);
      } catch (error) {
        void 0;
      }
    },
    [changePassword, reset],
  );

  const handleCancel = useCallback(() => {
    reset();
  }, [reset]);

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4" noValidate>
      <FormField
        label="Current Password"
        error={errors.current_password?.message}
        required
      >
        <PasswordInput
          id="current-password"
          {...register("current_password")}
          ref={currentPasswordRef}
          placeholder="Enter your current password"
          disabled={isSubmitting}
          aria-invalid={!!errors.current_password}
          aria-describedby={
            errors.current_password ? "current-password-error" : undefined
          }
        />
      </FormField>

      <FormField
        label="New Password"
        error={errors.new_password?.message}
        required
      >
        <PasswordInput
          id="new-password"
          {...register("new_password")}
          placeholder="Enter your new password"
          disabled={isSubmitting}
          aria-invalid={!!errors.new_password}
          aria-describedby={
            errors.new_password ? "new-password-error" : undefined
          }
        />
      </FormField>

      <FormField
        label="Confirm New Password"
        error={errors.confirm_password?.message}
        required
      >
        <PasswordInput
          id="confirm-password"
          {...register("confirm_password")}
          placeholder="Confirm your new password"
          disabled={isSubmitting}
          aria-invalid={!!errors.confirm_password}
          aria-describedby={
            errors.confirm_password ? "confirm-password-error" : undefined
          }
        />
      </FormField>

      <div className="flex items-center gap-3 pt-4">
        <Button
          type="submit"
          disabled={isSubmitting || !isDirty}
          className="flex-1"
          aria-busy={isSubmitting}
        >
          {isSubmitting ? "Changing..." : "Change Password"}
        </Button>
        <Button
          type="button"
          variant="outline"
          onClick={handleCancel}
          disabled={isSubmitting}
          className="flex-1"
        >
          Cancel
        </Button>
      </div>

      {isSuccess && (
        <div
          className="flex items-center gap-2 text-sm text-green-600 dark:text-green-400"
          role="status"
          aria-live="polite"
        >
          <Check className="w-4 h-4" aria-hidden="true" />
          <span>Password changed successfully</span>
        </div>
      )}

      {changePassword.error && (
        <div
          className="flex items-center gap-2 text-sm text-destructive"
          role="alert"
          aria-live="assertive"
        >
          <X className="w-4 h-4" aria-hidden="true" />
          <span>
            Failed to change password. Please check your current password and
            try again.
          </span>
        </div>
      )}
    </form>
  );
}
