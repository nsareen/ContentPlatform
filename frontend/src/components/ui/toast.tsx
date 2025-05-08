"use client";

import * as React from "react";

export interface ToastProps {
  title?: string;
  description?: string;
  type?: "default" | "success" | "error" | "warning";
  duration?: number;
}

const ToastContext = React.createContext<{
  toast: (props: ToastProps) => void;
}>({
  toast: () => {},
});

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const toast = (props: ToastProps) => {
    console.log("Toast:", props);
    // In a real implementation, this would show a toast notification
  };

  return (
    <ToastContext.Provider value={{ toast }}>
      {children}
    </ToastContext.Provider>
  );
}

export const useToast = () => {
  const context = React.useContext(ToastContext);
  if (!context) {
    throw new Error("useToast must be used within a ToastProvider");
  }
  return context;
};

export const toast = {
  error: (message: string) => {
    console.error("Toast error:", message);
  },
  success: (message: string) => {
    console.log("Toast success:", message);
  },
  warning: (message: string) => {
    console.warn("Toast warning:", message);
  },
  info: (message: string) => {
    console.info("Toast info:", message);
  },
};
