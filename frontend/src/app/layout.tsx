import type { Metadata } from "next";
import { Inter, Roboto } from "next/font/google";
import "./globals.css";
import { QueryProvider } from "@/lib/providers/query-provider";
import { AuthCheck } from "@/components/auth/auth-check";
import { Header } from "@/components/ui/header";
import { Sidebar } from "@/components/ui/sidebar";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
});

const roboto = Roboto({
  weight: ["300", "400", "500", "700"],
  subsets: ["latin"],
  variable: "--font-roboto",
});

export const metadata: Metadata = {
  title: "Content Platform | Brand Voice Studio",
  description: "Enterprise Content Platform with Brand Voice Studio capabilities",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${inter.variable} ${roboto.variable} font-sans antialiased`}>
        <QueryProvider>
          <AuthCheck>
            <div className="flex min-h-screen bg-gray-50">
              <Header />
              <Sidebar />
              <main className="flex-1 pt-14 pl-64 transition-all duration-300 ease-in-out">
                <div className="container mx-auto px-4 py-6">
                  {children}
                </div>
              </main>
            </div>
          </AuthCheck>
        </QueryProvider>
      </body>
    </html>
  );
}
