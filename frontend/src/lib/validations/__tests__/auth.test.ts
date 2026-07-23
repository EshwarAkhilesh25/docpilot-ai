import { describe, it, expect } from "vitest";
import { loginSchema, registerSchema } from "../auth";

describe("loginSchema", () => {
  it("should validate valid login data", () => {
    const validData = {
      email: "test@example.com",
      password: "password123",
    };
    const result = loginSchema.safeParse(validData);
    expect(result.success).toBe(true);
  });

  it("should reject empty email", () => {
    const invalidData = {
      email: "",
      password: "password123",
    };
    const result = loginSchema.safeParse(invalidData);
    expect(result.success).toBe(false);
    if (!result.success) {
      expect(result.error.errors[0].message).toBe("Email is required");
    }
  });

  it("should reject invalid email format", () => {
    const invalidData = {
      email: "invalid-email",
      password: "password123",
    };
    const result = loginSchema.safeParse(invalidData);
    expect(result.success).toBe(false);
    if (!result.success) {
      expect(result.error.errors[0].message).toBe("Invalid email address");
    }
  });

  it("should reject empty password", () => {
    const invalidData = {
      email: "test@example.com",
      password: "",
    };
    const result = loginSchema.safeParse(invalidData);
    expect(result.success).toBe(false);
    if (!result.success) {
      expect(result.error.errors[0].message).toBe("Password is required");
    }
  });
});

describe("registerSchema", () => {
  it("should validate valid registration data", () => {
    const validData = {
      name: "John Doe",
      email: "test@example.com",
      password: "Password123",
      confirmPassword: "Password123",
    };
    const result = registerSchema.safeParse(validData);
    expect(result.success).toBe(true);
  });

  it("should reject empty name", () => {
    const invalidData = {
      name: "",
      email: "test@example.com",
      password: "Password123",
      confirmPassword: "Password123",
    };
    const result = registerSchema.safeParse(invalidData);
    expect(result.success).toBe(false);
  });

  it("should reject name less than 2 characters", () => {
    const invalidData = {
      name: "J",
      email: "test@example.com",
      password: "Password123",
      confirmPassword: "Password123",
    };
    const result = registerSchema.safeParse(invalidData);
    expect(result.success).toBe(false);
  });

  it("should reject invalid email format", () => {
    const invalidData = {
      name: "John Doe",
      email: "invalid-email",
      password: "Password123",
      confirmPassword: "Password123",
    };
    const result = registerSchema.safeParse(invalidData);
    expect(result.success).toBe(false);
  });

  it("should reject password less than 8 characters", () => {
    const invalidData = {
      name: "John Doe",
      email: "test@example.com",
      password: "Pass1",
      confirmPassword: "Pass1",
    };
    const result = registerSchema.safeParse(invalidData);
    expect(result.success).toBe(false);
  });

  it("should reject password without uppercase letter", () => {
    const invalidData = {
      name: "John Doe",
      email: "test@example.com",
      password: "password123",
      confirmPassword: "password123",
    };
    const result = registerSchema.safeParse(invalidData);
    expect(result.success).toBe(false);
  });

  it("should reject password without lowercase letter", () => {
    const invalidData = {
      name: "John Doe",
      email: "test@example.com",
      password: "PASSWORD123",
      confirmPassword: "PASSWORD123",
    };
    const result = registerSchema.safeParse(invalidData);
    expect(result.success).toBe(false);
  });

  it("should reject password without number", () => {
    const invalidData = {
      name: "John Doe",
      email: "test@example.com",
      password: "Password",
      confirmPassword: "Password",
    };
    const result = registerSchema.safeParse(invalidData);
    expect(result.success).toBe(false);
  });

  it("should reject mismatched passwords", () => {
    const invalidData = {
      name: "John Doe",
      email: "test@example.com",
      password: "Password123",
      confirmPassword: "Password456",
    };
    const result = registerSchema.safeParse(invalidData);
    expect(result.success).toBe(false);
    if (!result.success) {
      expect(result.error.errors[0].message).toBe("Passwords do not match");
    }
  });

  it("should reject empty confirm password", () => {
    const invalidData = {
      name: "John Doe",
      email: "test@example.com",
      password: "Password123",
      confirmPassword: "",
    };
    const result = registerSchema.safeParse(invalidData);
    expect(result.success).toBe(false);
  });
});
