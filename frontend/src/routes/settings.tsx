import { useState } from "react";
import { motion } from "framer-motion";
import { Edit2 } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { DashboardLayout } from "@components/layout/DashboardLayout";
import { SettingsHeader } from "@components/settings/SettingsHeader";
import { SettingsSection } from "@components/settings/SettingsSection";
import { ProfileCard } from "@components/settings/ProfileCard";
import { EditProfileForm } from "@components/settings/EditProfileForm";
import { ChangePasswordForm } from "@components/settings/ChangePasswordForm";
import { AppearanceSettings } from "@components/settings/AppearanceSettings";
import { AccountActions } from "@components/settings/AccountActions";
import { SettingsSkeleton } from "@components/settings/SettingsSkeleton";
import { ErrorBoundary } from "@components/common/ErrorBoundary";
import { PremiumBackground } from "@components/common/PremiumBackground";
import { Button } from "@components/common/Button";
import { pageTransition, staggerContainer } from "@lib/animations";
import { ROUTES } from "@lib/constants";
import { useCurrentUser } from "@hooks/useSettings";
import { useAuthStore } from "@store/authStore";

export default function Settings() {
  const [isEditingProfile, setIsEditingProfile] = useState(false);
  const navigate = useNavigate();
  const { data: user, isLoading, error } = useCurrentUser();

  if (isLoading) {
    return (
      <DashboardLayout>
        <PremiumBackground variant="subtle" />
        <motion.div
          variants={pageTransition}
          initial="initial"
          animate="animate"
          className="w-full min-h-screen"
          role="main"
          aria-label="Settings"
        >
          <SettingsSkeleton />
        </motion.div>
      </DashboardLayout>
    );
  }

  if (error || !user) {
    return (
      <DashboardLayout>
        <PremiumBackground variant="subtle" />
        <motion.div
          variants={pageTransition}
          initial="initial"
          animate="animate"
          className="w-full min-h-screen"
          role="main"
          aria-label="Settings"
        >
          <div className="text-center py-12 space-y-4">
            <p className="text-destructive">
              Failed to load settings. Please try again.
            </p>
            <Button
              variant="destructive"
              onClick={() => {
                useAuthStore.getState().logout();
                navigate(ROUTES.LOGIN);
              }}
            >
              Logout
            </Button>
          </div>
        </motion.div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <PremiumBackground variant="subtle" />
      <motion.div
        variants={pageTransition}
        initial="initial"
        animate="animate"
        exit="exit"
        className="w-full min-h-screen"
        role="main"
        aria-label="Settings"
      >
        <div className="space-y-8">
          {/* Header */}
          <ErrorBoundary>
            <section aria-labelledby="settings-heading">
              <SettingsHeader
                title="Settings"
                subtitle="Manage your account preferences and appearance"
              />
            </section>
          </ErrorBoundary>

          {/* Settings Sections */}
          <motion.div
            variants={staggerContainer}
            initial="initial"
            animate="animate"
            className="space-y-6"
          >
            {/* Profile Section */}
            <ErrorBoundary>
              <section aria-labelledby="profile-heading">
                <h2 id="profile-heading" className="sr-only">
                  Profile Settings
                </h2>
                <SettingsSection
                  title="Profile"
                  description="View and edit your profile information"
                >
                  {isEditingProfile ? (
                    <EditProfileForm
                      user={user!}
                      onCancel={() => setIsEditingProfile(false)}
                    />
                  ) : (
                    <div className="space-y-4">
                      <ProfileCard user={user!} />
                      <Button
                        variant="outline"
                        onClick={() => setIsEditingProfile(true)}
                        className="w-full sm:w-auto"
                      >
                        <Edit2 className="w-4 h-4 mr-2" />
                        Edit Profile
                      </Button>
                    </div>
                  )}
                </SettingsSection>
              </section>
            </ErrorBoundary>

            {/* Appearance Section */}
            <ErrorBoundary>
              <section aria-labelledby="appearance-heading">
                <h2 id="appearance-heading" className="sr-only">
                  Appearance Settings
                </h2>
                <SettingsSection
                  title="Appearance"
                  description="Customize your theme preference"
                >
                  <AppearanceSettings />
                </SettingsSection>
              </section>
            </ErrorBoundary>

            {/* Change Password Section */}
            <ErrorBoundary>
              <section aria-labelledby="change-password-heading">
                <h2 id="change-password-heading" className="sr-only">
                  Change Password
                </h2>
                <SettingsSection
                  title="Change Password"
                  description="Update your password to keep your account secure"
                >
                  <ChangePasswordForm />
                </SettingsSection>
              </section>
            </ErrorBoundary>

            {/* Account Section */}
            <ErrorBoundary>
              <section aria-labelledby="account-heading">
                <h2 id="account-heading" className="sr-only">
                  Account Actions
                </h2>
                <SettingsSection
                  title="Account"
                  description="Manage your account actions"
                >
                  <AccountActions />
                </SettingsSection>
              </section>
            </ErrorBoundary>
          </motion.div>
        </div>
      </motion.div>
    </DashboardLayout>
  );
}
