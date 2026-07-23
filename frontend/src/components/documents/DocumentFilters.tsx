import { ProcessingStatus } from "@services/documentService";

interface DocumentFiltersProps {
  value: ProcessingStatus | null;
  onChange: (value: ProcessingStatus | null) => void;
}

export function DocumentFilters({ value, onChange }: DocumentFiltersProps) {
  const filters = [
    { label: "All", value: null },
    { label: "Processing", value: ProcessingStatus.PROCESSING },
    { label: "Completed", value: ProcessingStatus.COMPLETED },
    { label: "Failed", value: ProcessingStatus.FAILED },
  ];

  return (
    <div
      className="flex items-center space-x-2"
      role="group"
      aria-label="Document filters"
    >
      {filters.map((filter) => (
        <button
          key={filter.label}
          onClick={() => onChange(filter.value)}
          className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
            value === filter.value
              ? "bg-primary text-primary-foreground"
              : "bg-muted text-muted-foreground hover:bg-muted/80 hover:text-foreground"
          }`}
          aria-pressed={value === filter.value}
          aria-label={`Filter by ${filter.label}`}
        >
          {filter.label}
        </button>
      ))}
    </div>
  );
}
