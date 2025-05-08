'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from "next/link";
import { authService } from '@/lib/api/auth-service';

export default function Home() {
  const router = useRouter();
  
  useEffect(() => {
    // Check if user is authenticated and redirect to brand voices page
    if (authService.isAuthenticated()) {
      router.push('/brand-voices');
    }
  }, [router]);
  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="bg-white border-b border-border-default px-6 py-4">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <h1 className="text-xl font-semibold text-text-primary">Content Platform</h1>
          <nav className="flex items-center space-x-4">
            <Link href="/brand-voices" className="text-text-secondary hover:text-text-primary">
              Brand Voices
            </Link>
            <Link href="/projects" className="text-text-secondary hover:text-text-primary">
              Projects
            </Link>
            <Link href="/settings" className="text-text-secondary hover:text-text-primary">
              Settings
            </Link>
          </nav>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-semibold text-text-primary">My Desk</h2>
            <Link
              href="/brand-voices/new"
              className="btn-primary"
            >
              Create Brand Voice
            </Link>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div className="card">
              <h3 className="text-lg font-medium mb-2 text-text-primary">Quick Start</h3>
              <p className="text-text-secondary mb-4">
                Create a new brand voice or manage existing ones to power your content generation.
              </p>
              <Link
                href="/brand-voices"
                className="text-primary font-medium hover:underline inline-flex items-center"
              >
                View Brand Voices
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
                  className="ml-1"
                >
                  <path d="m9 18 6-6-6-6" />
                </svg>
              </Link>
            </div>

            <div className="card">
              <h3 className="text-lg font-medium mb-2 text-text-primary">Recent Projects</h3>
              <p className="text-text-secondary mb-4">
                Access your recent content projects and track their progress.
              </p>
              <Link
                href="/projects"
                className="text-primary font-medium hover:underline inline-flex items-center"
              >
                View Projects
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
                  className="ml-1"
                >
                  <path d="m9 18 6-6-6-6" />
                </svg>
              </Link>
            </div>

            <div className="card">
              <h3 className="text-lg font-medium mb-2 text-text-primary">My Tasks</h3>
              <p className="text-text-secondary mb-4">
                View and manage your assigned tasks and content reviews.
              </p>
              <Link
                href="/tasks"
                className="text-primary font-medium hover:underline inline-flex items-center"
              >
                View Tasks
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
                  className="ml-1"
                >
                  <path d="m9 18 6-6-6-6" />
                </svg>
              </Link>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
