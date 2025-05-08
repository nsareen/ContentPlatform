import { useState } from "react";
import Link from "next/link";

interface HeaderProps {
  user?: {
    name: string;
    email: string;
    avatar?: string;
  };
}

export function Header({ user }: HeaderProps) {
  const [isProfileOpen, setIsProfileOpen] = useState(false);

  return (
    <header className="h-14 border-b border-border bg-white flex items-center justify-between px-4">
      <div className="flex items-center">
        <div className="relative w-[280px]">
          <input
            type="text"
            placeholder="What are you looking for..."
            className="w-full h-9 px-3 py-2 text-sm border border-border rounded-md focus:outline-none focus:ring-1 focus:ring-[#6D3BEB]"
          />
          <div className="absolute right-3 top-1/2 transform -translate-y-1/2 text-[#94A3B8]">
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
      </div>
      <div className="flex items-center gap-4">
        <button className="h-9 px-4 rounded-md bg-white text-[#6D3BEB] border border-[#6D3BEB] text-sm font-medium">
          Create
        </button>
        <div className="relative">
          <button
            className="flex items-center"
            onClick={() => setIsProfileOpen(!isProfileOpen)}
          >
            <div className="w-8 h-8 rounded-full bg-[#6D3BEB] text-white flex items-center justify-center text-sm font-medium">
              {user?.name?.charAt(0) || "U"}
            </div>
          </button>
          {isProfileOpen && (
            <div className="absolute right-0 mt-2 w-48 bg-white border border-border rounded-md shadow-md z-10">
              <div className="p-3 border-b border-border">
                <p className="font-medium">{user?.name || "User"}</p>
                <p className="text-sm text-[#475569]">{user?.email || "user@example.com"}</p>
              </div>
              <div className="p-2">
                <Link
                  href="/profile"
                  className="block px-3 py-2 text-sm rounded-md hover:bg-[#F8FAFC]"
                >
                  Profile
                </Link>
                <Link
                  href="/settings"
                  className="block px-3 py-2 text-sm rounded-md hover:bg-[#F8FAFC]"
                >
                  Settings
                </Link>
                <button className="w-full text-left px-3 py-2 text-sm text-red-500 rounded-md hover:bg-[#F8FAFC]">
                  Sign out
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
