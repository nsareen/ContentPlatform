import Link from "next/link";
import { ReactNode } from "react";

export default function BrandVoicesLayout({
  children,
}: {
  children: ReactNode;
}) {
  return (
    <div className="min-h-screen bg-background">
      <header className="border-b border-border-default bg-white">
        <div className="container mx-auto px-4 py-4">
          <div className="flex-between">
            <div>
              <h1 className="text-2xl font-semibold text-text-primary">Brand Voice Studio</h1>
              <p className="text-sm text-text-secondary">Manage your brand voice profiles</p>
            </div>
            <Link href="/brand-voices/new" className="btn-primary">
              Create Brand Voice
            </Link>
          </div>
        </div>
      </header>
      
      <nav className="bg-white border-b border-border-default">
        <div className="container mx-auto px-4">
          <div className="flex space-x-6">
            <Link 
              href="/brand-voices" 
              className="py-3 text-sm font-medium border-b-2 border-primary text-primary"
            >
              Brand Voices
            </Link>
            <Link 
              href="/templates" 
              className="py-3 text-sm font-medium border-b-2 border-transparent text-text-secondary hover:text-text-primary"
            >
              Templates
            </Link>
            <Link 
              href="/analytics" 
              className="py-3 text-sm font-medium border-b-2 border-transparent text-text-secondary hover:text-text-primary"
            >
              Analytics
            </Link>
          </div>
        </div>
      </nav>
      
      <main className="container mx-auto px-4 py-6">
        {children}
      </main>
    </div>
  );
}
