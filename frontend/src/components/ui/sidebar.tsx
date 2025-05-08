"use client";

import React, { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import { 
  ChevronLeft, 
  ChevronRight, 
  Home, 
  MessageSquare, 
  Globe, 
  FileText, 
  Settings, 
  Plug, 
  Users
} from 'lucide-react';

type NavItem = {
  name: string;
  href: string;
  icon: React.ElementType;
};

const navItems: NavItem[] = [
  { name: 'Dashboard', href: '/', icon: Home },
  { name: 'Brand Voices', href: '/brand-voices', icon: MessageSquare },
  { name: 'Language Pairs', href: '/language-pairs', icon: Globe },
  { name: 'Localization Templates', href: '/localization-templates', icon: FileText },
  { name: 'Content Projects', href: '/content-projects', icon: FileText },
  { name: 'Admin', href: '/admin', icon: Users },
  { name: 'Configurations', href: '/configurations', icon: Settings },
  { name: 'Connectors', href: '/connectors', icon: Plug },
];

export function Sidebar() {
  const pathname = usePathname();
  const [collapsed, setCollapsed] = useState(false);

  return (
    <div 
      className={cn(
        "h-screen fixed top-0 left-0 z-40 flex flex-col border-r border-gray-200 bg-white transition-all duration-300 ease-in-out",
        collapsed ? "w-16" : "w-64"
      )}
      style={{ paddingTop: '56px' }} // Account for the header height
    >
      <div className="flex items-center justify-end p-2">
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="p-1 rounded-md hover:bg-gray-100 text-gray-500"
          aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
        >
          {collapsed ? <ChevronRight size={20} /> : <ChevronLeft size={20} />}
        </button>
      </div>
      
      <nav className="flex-1 overflow-y-auto">
        <ul className="space-y-1 px-2">
          {navItems.map((item) => {
            const isActive = pathname === item.href || pathname.startsWith(`${item.href}/`);
            
            return (
              <li key={item.name}>
                <Link
                  href={item.href}
                  className={cn(
                    "flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors",
                    isActive 
                      ? "text-[#6D3BEB] bg-[#F5F0FF] border-l-4 border-[#6D3BEB]" 
                      : "text-gray-700 hover:bg-gray-100",
                    collapsed && "justify-center"
                  )}
                >
                  <item.icon size={20} className={cn("flex-shrink-0", collapsed ? "" : "mr-3")} />
                  {!collapsed && <span>{item.name}</span>}
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>
      
      <div className="p-4 border-t border-gray-200">
        {!collapsed && (
          <div className="text-xs text-gray-500">
            <p>Content Platform v1.0</p>
          </div>
        )}
      </div>
    </div>
  );
}
