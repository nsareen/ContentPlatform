import { useState } from "react";
import Link from "next/link";
import { BrandVoiceCard, BrandVoice } from "./brand-voice-card";

interface BrandVoiceListProps {
  voices: BrandVoice[];
  onEdit?: (voice: BrandVoice) => void;
  onDelete?: (voice: BrandVoice) => void;
  onPublish?: (voice: BrandVoice) => void;
}

export function BrandVoiceList({ voices, onEdit, onDelete, onPublish }: BrandVoiceListProps) {
  const [viewMode, setViewMode] = useState<"grid" | "list">("grid");
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [sortBy, setSortBy] = useState<string>("name");

  // Filter voices based on search query and status filter
  const filteredVoices = voices.filter((voice) => {
    const matchesSearch = voice.name.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = statusFilter === "all" || voice.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  // Function to format date in a readable format
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  // Sort voices based on sort criteria
  const sortedVoices = [...filteredVoices].sort((a, b) => {
    switch (sortBy) {
      case "name":
        return a.name.localeCompare(b.name);
      case "status":
        return a.status.localeCompare(b.status);
      case "version":
        return b.version - a.version;
      case "date":
        return new Date(b.updated_at || b.created_at).getTime() - new Date(a.updated_at || a.created_at).getTime();
      default:
        return 0;
    }
  });

  return (
    <div>
      <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-2">
          <div className="relative w-64">
            <input
              type="text"
              placeholder="Search brand voices..."
              className="input h-9 text-sm"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
            <div className="absolute right-3 top-1/2 transform -translate-y-1/2 text-text-tertiary">
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
              >
                <circle cx="11" cy="11" r="8" />
                <path d="m21 21-4.3-4.3" />
              </svg>
            </div>
          </div>
          <div className="relative">
            <select
              className="input h-9 text-sm appearance-none pr-8"
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
            >
              <option value="all">All Statuses</option>
              <option value="draft">Draft</option>
              <option value="published">Published</option>
              <option value="under_review">Under Review</option>
              <option value="inactive">Inactive</option>
            </select>
            <div className="absolute right-3 top-1/2 transform -translate-y-1/2 text-text-tertiary pointer-events-none">
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
              >
                <path d="m6 9 6 6 6-6" />
              </svg>
            </div>
          </div>
          <div className="relative">
            <select
              className="input h-9 text-sm appearance-none pr-8"
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
            >
              <option value="name">Sort by Name</option>
              <option value="status">Sort by Status</option>
              <option value="version">Sort by Version</option>
              <option value="date">Sort by Date</option>
            </select>
            <div className="absolute right-3 top-1/2 transform -translate-y-1/2 text-text-tertiary pointer-events-none">
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
              >
                <path d="m6 9 6 6 6-6" />
              </svg>
            </div>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button
            className={`p-2 rounded-md ${
              viewMode === "grid" ? "bg-primary bg-opacity-10 text-primary" : "text-text-secondary hover:bg-background-surface"
            }`}
            onClick={() => setViewMode("grid")}
            aria-label="Grid view"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="18"
              height="18"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <rect width="7" height="7" x="3" y="3" rx="1" />
              <rect width="7" height="7" x="14" y="3" rx="1" />
              <rect width="7" height="7" x="14" y="14" rx="1" />
              <rect width="7" height="7" x="3" y="14" rx="1" />
            </svg>
          </button>
          <button
            className={`p-2 rounded-md ${
              viewMode === "list" ? "bg-primary bg-opacity-10 text-primary" : "text-text-secondary hover:bg-background-surface"
            }`}
            onClick={() => setViewMode("list")}
            aria-label="List view"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="18"
              height="18"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <line x1="8" y1="6" x2="21" y2="6" />
              <line x1="8" y1="12" x2="21" y2="12" />
              <line x1="8" y1="18" x2="21" y2="18" />
              <line x1="3" y1="6" x2="3.01" y2="6" />
              <line x1="3" y1="12" x2="3.01" y2="12" />
              <line x1="3" y1="18" x2="3.01" y2="18" />
            </svg>
          </button>
        </div>
      </div>

      {sortedVoices.length === 0 ? (
        <div className="text-center py-12 card">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="48"
            height="48"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
            className="mx-auto text-text-tertiary mb-4"
          >
            <rect width="18" height="18" x="3" y="3" rx="2" />
            <path d="M7 7h.01" />
            <path d="M17 7h.01" />
            <path d="M7 17h.01" />
            <path d="M17 17h.01" />
          </svg>
          <h3 className="text-lg font-medium mb-2">No brand voices found</h3>
          <p className="text-text-secondary mb-4">
            {searchQuery || statusFilter !== "all"
              ? "Try adjusting your search or filters"
              : "Create your first brand voice to get started"}
          </p>
          <button className="btn-primary">
            Create Brand Voice
          </button>
        </div>
      ) : viewMode === "grid" ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {sortedVoices.map((voice) => (
            <BrandVoiceCard
              key={voice.id}
              voice={voice}
              onEdit={onEdit}
              onDelete={onDelete}
              onPublish={onPublish}
            />
          ))}
        </div>
      ) : (
        <div className="border border-border-default rounded-md overflow-hidden">
          <table className="w-full bg-white">
            <thead>
              <tr className="border-b border-border-default bg-background-surface">
                <th className="px-4 py-3 text-left text-xs font-medium text-text-secondary uppercase tracking-wider">
                  Name
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-text-secondary uppercase tracking-wider">
                  Description
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-text-secondary uppercase tracking-wider">
                  Status
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-text-secondary uppercase tracking-wider">
                  Version
                </th>
                <th className="px-4 py-3 text-left text-xs font-medium text-text-secondary uppercase tracking-wider">
                  Last Updated
                </th>
                <th className="px-4 py-3 text-right text-xs font-medium text-text-secondary uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody>
              {sortedVoices.map((voice) => (
                <tr key={voice.id} className="border-b border-border-default">
                  <td className="px-4 py-3 whitespace-nowrap">
                    <div className="flex items-center">
                      <div className="w-8 h-8 rounded-md bg-primary flex-center text-white mr-3">
                        {voice.name.charAt(0)}
                      </div>
                      <Link
                        href={`/brand-voices/${voice.id}`}
                        className="font-medium hover:text-primary"
                      >
                        {voice.name}
                      </Link>
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    <p className="text-sm text-text-secondary line-clamp-1">{voice.description}</p>
                  </td>
                  <td className="px-4 py-3">
                    <span
                      className={`badge ${voice.status === "draft" ? "badge-draft" : voice.status === "published" ? "badge-published" : voice.status === "under_review" ? "badge-review" : "badge-inactive"}`}
                    >
                      {voice.status.charAt(0).toUpperCase() + voice.status.slice(1)}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-sm text-text-secondary">v{voice.version}</td>
                  <td className="px-4 py-3 text-sm text-text-secondary">
                    {voice.updated_at
                      ? new Date(voice.updated_at).toLocaleDateString()
                      : new Date(voice.created_at).toLocaleDateString()}
                  </td>
                  <td className="px-4 py-3 text-right">
                    <div className="flex items-center justify-end gap-2">
                      <button
                        className="p-1 rounded-md hover:bg-background-surface"
                        onClick={() => onEdit?.(voice)}
                        aria-label="Edit"
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
                          <path d="M17 3a2.85 2.85 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5Z" />
                          <path d="m15 5 4 4" />
                        </svg>
                      </button>
                      {voice.status === "draft" && (
                        <button
                          className="p-1 rounded-md hover:bg-background-surface"
                          onClick={() => onPublish?.(voice)}
                          aria-label="Publish"
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
                            <path d="M12 2v20" />
                            <path d="m19 15-7 7-7-7" />
                          </svg>
                        </button>
                      )}
                      <button
                        className="p-1 rounded-md hover:bg-background-surface"
                        onClick={() => onDelete?.(voice)}
                        aria-label="Delete"
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
                          className="text-feedback-error"
                        >
                          <path d="M3 6h18" />
                          <path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6" />
                          <path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2" />
                          <line x1="10" x2="10" y1="11" y2="17" />
                          <line x1="14" x2="14" y1="11" y2="17" />
                        </svg>
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
