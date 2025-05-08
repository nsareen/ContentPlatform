'use client';

import { useEffect, useState } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { authService } from '@/lib/api/auth-service';

interface AuthCheckProps {
  children: React.ReactNode;
}

export function AuthCheck({ children }: AuthCheckProps) {
  const router = useRouter();
  const pathname = usePathname();
  const [isChecking, setIsChecking] = useState(true);

  useEffect(() => {
    const initializeAuth = async () => {
      try {
        // Initialize auth from localStorage
        authService.initAuth();
        
        // Check if user is authenticated
        const isAuthenticated = authService.isAuthenticated();
        console.log('Auth check - authenticated:', isAuthenticated);
        
        // Public routes that don't require authentication
        const publicRoutes = ['/login'];
        const isPublicRoute = publicRoutes.includes(pathname) || pathname === '/';
        
        if (!isAuthenticated && !isPublicRoute) {
          // Redirect to login if not authenticated and not on a public route
          console.log('Not authenticated, redirecting to login');
          router.push('/login');
        } else if (isAuthenticated && pathname === '/login') {
          // Redirect to brand voices if already authenticated and on login page
          console.log('Already authenticated, redirecting to brand voices');
          router.push('/brand-voices');
        }
      } catch (error) {
        console.error('Error in auth check:', error);
      } finally {
        setIsChecking(false);
      }
    };
    
    initializeAuth();
  }, [pathname, router]);

  // Show nothing while checking authentication
  if (isChecking) {
    return null;
  }

  return <>{children}</>;
}
