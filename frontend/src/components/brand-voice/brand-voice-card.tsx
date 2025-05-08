import { useState } from "react";
import Link from "next/link";

export interface BrandVoice {
  id: string;
  name: string;
  description: string;
  status: "draft" | "published" | "under_review" | "inactive";
  version: number;
  created_at: string;
  updated_at?: string;
  dos?: string;
  donts?: string;
  voice_metadata?: {
    personality?: string;
    tonality?: string;
  };
}

interface BrandVoiceCardProps {
  voice: BrandVoice;
  onEdit?: (voice: BrandVoice) => void;
  onDelete?: (voice: BrandVoice) => void;
  onPublish?: (voice: BrandVoice) => void;
}

export function BrandVoiceCard({ voice, onEdit, onDelete, onPublish }: BrandVoiceCardProps) {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const getStatusColor = (status: BrandVoice["status"]) => {
    switch (status) {
      case "draft":
        return "bg-yellow-100 text-yellow-800";
      case "published":
        return "bg-green-100 text-green-800";
      case "under_review":
        return "bg-blue-100 text-blue-800";
      case "inactive":
        return "bg-gray-100 text-gray-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
    }).format(date);
  };

  return (
    <div className="card hover:shadow-md transition-shadow">
      <div className="p-4">
        <div className="flex-between">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <div className="w-8 h-8 rounded-md bg-primary flex-center text-white">
                {voice.name.charAt(0)}
              </div>
              <Link href={`/brand-voices/${voice.id}`} className="font-medium hover:text-primary">
                {voice.name}
              </Link>
            </div>
            <p className="text-sm text-text-secondary line-clamp-2 mb-3">{voice.description}</p>
          </div>
          <div className="relative">
            <button
              className="p-1 rounded-md hover:bg-background-surface"
              onClick={() => setIsMenuOpen(!isMenuOpen)}
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                className="text-text-secondary"
              >
                <circle cx="12" cy="12" r="1" />
                <circle cx="12" cy="5" r="1" />
                <circle cx="12" cy="19" r="1" />
              </svg>
            </button>
            {isMenuOpen && (
              <div className="absolute right-0 mt-1 w-36 bg-white border border-border-default rounded-md shadow-md z-10">
                <div className="p-1">
                  <button
                    className="w-full text-left px-3 py-2 text-sm rounded-md hover:bg-background-surface flex items-center"
                    onClick={() => {
                      onEdit?.(voice);
                      setIsMenuOpen(false);
                    }}
                  >
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      width="14"
                      height="14"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      className="mr-2"
                    >
                      <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" />
                      <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" />
                    </svg>
                    Edit
                  </button>
                  {voice.status === "draft" && (
                    <button
                      className="w-full text-left px-3 py-2 text-sm rounded-md hover:bg-background-surface flex items-center"
                      onClick={() => {
                        onPublish?.(voice);
                        setIsMenuOpen(false);
                      }}
                    >
                      <svg
                        xmlns="http://www.w3.org/2000/svg"
                        width="14"
                        height="14"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        className="mr-2"
                      >
                        <path d="M12 2v4" />
                        <path d="m6.343 6.343-2.828-2.828" />
                        <path d="M2 12h4" />
                        <path d="m6.343 17.657-2.828 2.828" />
                        <path d="M12 22v-4" />
                        <path d="m17.657 17.657 2.828 2.828" />
                        <path d="M22 12h-4" />
                        <path d="m17.657 6.343 2.828-2.828" />
                      </svg>
                      Publish
                    </button>
                  )}
                  <button
                    className="w-full text-left px-3 py-2 text-sm rounded-md hover:bg-background-surface text-feedback-error flex items-center"
                    onClick={() => {
                      onDelete?.(voice);
                      setIsMenuOpen(false);
                    }}
                  >
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      width="14"
                      height="14"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      className="mr-2"
                    >
                      <path d="M3 6h18" />
                      <path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6" />
                      <path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2" />
                      <line x1="10" y1="11" x2="10" y2="17" />
                      <line x1="14" y1="11" x2="14" y2="17" />
                    </svg>
                    Delete
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
        <div className="flex-between mt-4 text-xs">
          <div className="flex items-center gap-2">
            <span className={`badge ${voice.status === "draft" ? "badge-draft" : voice.status === "published" ? "badge-published" : voice.status === "under_review" ? "badge-review" : "badge-inactive"}`}>
              {voice.status.charAt(0).toUpperCase() + voice.status.slice(1)}
            </span>
            <span className="text-text-tertiary">v{voice.version}</span>
          </div>
          <span className="text-text-tertiary">
            {voice.updated_at
              ? `Updated ${formatDate(voice.updated_at)}`
              : `Created ${formatDate(voice.created_at)}`}
          </span>
        </div>
      </div>
    </div>
  );
}
