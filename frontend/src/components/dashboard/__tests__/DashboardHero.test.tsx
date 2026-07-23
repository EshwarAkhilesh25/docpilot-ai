import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { DashboardHero } from "../DashboardHero";

describe("DashboardHero", () => {
  it("should render greeting with user name", () => {
    render(<DashboardHero userName="John Doe" />);
    expect(screen.getByText(/John Doe/)).toBeInTheDocument();
  });

  it("should render current time", () => {
    render(<DashboardHero userName="User" />);
    // Check that time is rendered (format will vary)
    expect(screen.getByText(/AM|PM/)).toBeInTheDocument();
  });

  it("should render welcome message", () => {
    render(<DashboardHero userName="User" />);
    expect(screen.getByText(/Welcome back/)).toBeInTheDocument();
  });
});
