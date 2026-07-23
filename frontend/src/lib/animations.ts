import { Variants } from "framer-motion";
import { ANIMATION_DURATION } from "./constants";

// Check for reduced motion preference
const prefersReducedMotion = () => {
  if (typeof window === "undefined") return false;
  return window.matchMedia("(prefers-reduced-motion: reduce)").matches;
};

// Page transitions
export const pageTransition: Variants = {
  initial: { opacity: 0, y: 20 },
  animate: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -20 },
};

export const pageTransitionProps = {
  transition: {
    duration: prefersReducedMotion() ? 0 : ANIMATION_DURATION.SLOW / 1000,
  },
};

// Card animations
export const cardVariants: Variants = {
  initial: { opacity: 0, scale: 0.95 },
  animate: { opacity: 1, scale: 1 },
  exit: { opacity: 0, scale: 0.95 },
};

// Dialog animations
export const dialogVariants: Variants = {
  initial: { opacity: 0, scale: 0.9 },
  animate: { opacity: 1, scale: 1 },
  exit: { opacity: 0, scale: 0.9 },
};

// Button hover animation
export const buttonHover = {
  scale: prefersReducedMotion() ? 1 : 1.02,
  transition: {
    duration: prefersReducedMotion() ? 0 : ANIMATION_DURATION.NORMAL / 1000,
  },
};

// List item animations
export const listItemVariants: Variants = {
  initial: { opacity: 0, x: -20 },
  animate: { opacity: 1, x: 0 },
  exit: { opacity: 0, x: 20 },
};

// Upload animation
export const uploadVariants: Variants = {
  initial: { opacity: 0, scale: 0.8 },
  animate: { opacity: 1, scale: 1 },
  exit: { opacity: 0, scale: 0.8 },
};

// Fade animation
export const fadeVariants: Variants = {
  initial: { opacity: 0 },
  animate: { opacity: 1 },
  exit: { opacity: 0 },
};

// Stagger children for lists
export const staggerContainer: Variants = {
  animate: {
    transition: {
      staggerChildren: prefersReducedMotion() ? 0 : 0.1,
    },
  },
};

// Route transition variants
export const routeTransition = {
  fadeIn: {
    initial: { opacity: 0 },
    animate: { opacity: 1 },
    exit: { opacity: 0 },
    transition: {
      duration: prefersReducedMotion() ? 0 : ANIMATION_DURATION.NORMAL / 1000,
    },
  },
  slideIn: {
    initial: { opacity: 0, x: 20 },
    animate: { opacity: 1, x: 0 },
    exit: { opacity: 0, x: -20 },
    transition: {
      duration: prefersReducedMotion() ? 0 : ANIMATION_DURATION.NORMAL / 1000,
    },
  },
  scaleIn: {
    initial: { opacity: 0, scale: 0.95 },
    animate: { opacity: 1, scale: 1 },
    exit: { opacity: 0, scale: 0.95 },
    transition: {
      duration: prefersReducedMotion() ? 0 : ANIMATION_DURATION.NORMAL / 1000,
    },
  },
  slideUp: {
    initial: { opacity: 0, y: 20 },
    animate: { opacity: 1, y: 0 },
    exit: { opacity: 0, y: -20 },
    transition: {
      duration: prefersReducedMotion() ? 0 : ANIMATION_DURATION.NORMAL / 1000,
    },
  },
};

// Micro-interaction variants
export const microInteractions = {
  button: {
    hover: { scale: prefersReducedMotion() ? 1 : 1.02 },
    tap: { scale: prefersReducedMotion() ? 1 : 0.98 },
    disabled: { scale: 1, opacity: 0.5 },
    transition: { duration: prefersReducedMotion() ? 0 : 0.15 },
  },
  card: {
    hover: {
      y: prefersReducedMotion() ? 0 : -4,
      boxShadow:
        "0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)",
    },
    transition: { duration: prefersReducedMotion() ? 0 : 0.2 },
  },
  dropdown: {
    open: {
      opacity: 1,
      y: 0,
      transition: { duration: prefersReducedMotion() ? 0 : 0.15 },
    },
    closed: {
      opacity: 0,
      y: -10,
      transition: { duration: prefersReducedMotion() ? 0 : 0.15 },
    },
  },
  icon: {
    hover: {
      scale: prefersReducedMotion() ? 1 : 1.1,
      rotate: prefersReducedMotion() ? 0 : 5,
    },
    transition: { duration: prefersReducedMotion() ? 0 : 0.15 },
  },
};
