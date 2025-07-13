import { ChevronDown, ChevronUp } from "lucide-react";
import { useState } from "react";

interface PanelSectionProps {
  title: string;
  children: React.ReactNode;
  defaultOpen?: boolean;
  collapsible?: boolean;
}

export function PanelSection({
  title,
  children,
  defaultOpen = true,
  collapsible = true,
}: PanelSectionProps) {
  const [isOpen, setIsOpen] = useState(defaultOpen);

  return (
    <div className="border-b border-gray-200 pb-4 last:border-b-0">
      <div
        className={`flex items-center justify-between mb-3 ${
          collapsible ? "cursor-pointer" : ""
        }`}
        onClick={() => collapsible && setIsOpen(!isOpen)}
      >
        <h3 className="text-sm font-semibold text-gray-900">{title}</h3>
        {collapsible && (
          <button className="p-1 hover:bg-gray-100 rounded">
            {isOpen ? (
              <ChevronUp className="h-4 w-4 text-gray-500" />
            ) : (
              <ChevronDown className="h-4 w-4 text-gray-500" />
            )}
          </button>
        )}
      </div>
      {isOpen && <div>{children}</div>}
    </div>
  );
} 