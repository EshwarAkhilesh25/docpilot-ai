import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { DashboardStatCard } from "../DashboardStatCard";
import { FileText } from "lucide-react";

describe("DashboardStatCard", () => {
  it("should render title and value", () => {
    render(
      <DashboardStatCard
        title="Total Documents"
        value={42}
        icon={<FileText className="h-5 w-5" />}
        loading={false}
      />,
    );
    expect(screen.getByText("Total Documents")).toBeInTheDocument();
    expect(screen.getByText("42")).toBeInTheDocument();
  });

  it("should render loading state", () => {
    render(
      <DashboardStatCard
        title="Total Documents"
        value={42}
        icon={<FileText className="h-5 w-5" />}
        loading={true}
      />,
    );
    expect(screen.getByRole("status")).toBeInTheDocument();
  });

  it("should render icon", () => {
    const { container } = render(
      <DashboardStatCard
        title="Total Documents"
        value={42}
        icon={<FileText className="h-5 w-5" />}
        loading={false}
      />,
    );
    expect(container.querySelector("svg")).toBeInTheDocument();
  });
});
