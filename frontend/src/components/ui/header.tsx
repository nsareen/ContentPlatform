"use client";

import React from 'react';
import Link from 'next/link';
import { User, Bell, Search } from 'lucide-react';
import { cn } from '@/lib/utils';

export function Header() {
  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-white shadow-sm">
      <div className="relative">
        {/* Main header content */}
        <div className="flex h-14 items-center justify-between px-4">
          {/* Logo and brand */}
          <div className="flex items-center">
            <Link href="/" className="flex items-center">
              <span className="text-xl font-semibold text-[#6D3BEB]">Genome.AI</span>
              <span className="ml-2 text-xs bg-[#6D3BEB] text-white px-2 py-0.5 rounded">CPS</span>
            </Link>
          </div>

          {/* Search */}
          <div className="hidden md:flex items-center flex-1 max-w-md mx-4">
            <div className="relative w-full">
              <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
                <Search className="h-4 w-4 text-gray-400" />
              </div>
              <input
                type="text"
                className="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-[#6D3BEB] focus:border-[#6D3BEB] block w-full pl-10 p-2"
                placeholder="What are you looking for..."
              />
            </div>
          </div>

          {/* Right side icons */}
          <div className="flex items-center space-x-4">
            <button className="p-1 rounded-full hover:bg-gray-100">
              <Bell className="h-5 w-5 text-gray-600" />
            </button>
            <button className="p-1 rounded-full hover:bg-gray-100">
              <User className="h-5 w-5 text-gray-600" />
            </button>
          </div>
        </div>

        {/* Gradient border at bottom */}
        <div 
          className="absolute bottom-0 left-0 right-0 h-[2px]"
          style={{
            background: 'linear-gradient(90deg, #6D3BEB 0%, #8B63F9 50%, #5A26B8 100%)'
          }}
        />
      </div>
    </header>
  );
}
