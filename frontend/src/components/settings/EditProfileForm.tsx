import { useState, useEffect, useCallback } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { Check, X } from "lucide-react";
import {
  updateProfileSchema,
  UpdateProfileInput,
} from "@lib/validations/settings";
import { useUpdateProfile } from "@hooks/useSettings";
import { Button } from "@components/common/Button";
import { FormField } from "@components/auth/FormField";
import { User } from "@services/settingsService";

interface EditProfileFormProps {
  user: User;
  onCancel: () => void;
}

export function EditProfileForm({ user, onCancel }: EditProfileFormProps) {
  const [isSuccess, setIsSuccess] = useState(false);
  const updateProfile = useUpdateProfile();

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting, isDirty },
  } = useForm<UpdateProfileInput>({
    resolver: zodResolver(updateProfileSchema),
    defaultValues: {
      full_name: user.full_name,
    },
  });

  // Handle escape key to cancel
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === "Escape" && !isSubmitting) {
        onCancel();
      }
    };
    window.addEventListener("keydown", handleEscape);
    return () => window.removeEventListener("keydown", handleEscape);
  }, [onCancel, isSubmitting]);

  const onSubmit = useCallback(
    async (data: UpdateProfileInput) => {
      try {
        await updateProfile.mutateAsync(data);
        setIsSuccess(true);
        setTimeout(() => setIsSuccess(false), 3000);
      } catch (error) {
        void 0;
      }
    },
    [updateProfile],
  );

  const handleCancel = useCallback(() => {
    reset({ full_name: user.full_name });
    onCancel();
  }, [reset, user.full_name, onCancel]);

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4" noValidate>
      <FormField label="Full Name" error={errors.full_name?.message} required>
        <input
          type="text"
          id="full-name"
          {...register("full_name")}
          className="w-full px-3 py-2 rounded-lg border border-border bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent disabled:opacity-50 disabled:cursor-not-allowed"
          placeholder="Enter your full name"
          disabled={isSubmitting}
          aria-invalid={!!errors.full_name}
          aria-describedby={errors.full_name ? "full-name-error" : undefined}
        />
      </FormField>

      <div className="flex items-center gap-3 pt-4">
        <Button
          type="submit"
          disabled={isSubmitting || !isDirty}
          className="flex-1"
          aria-busy={isSubmitting}
        >
          {isSubmitting ? "Saving..." : "Save Changes"}
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
          <span>Profile updated successfully</span>
        </div>
      )}

      {updateProfile.isError && (
        <div
          className="flex items-center gap-2 text-sm text-destructive"
          role="alert"
          aria-live="assertive"
        >
          <X className="w-4 h-4" aria-hidden="true" />
          <span>Failed to update profile. Please try again.</span>
        </div>
      )}
    </form>
  );
}
