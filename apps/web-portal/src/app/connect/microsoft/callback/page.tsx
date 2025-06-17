"use client";

// If you see type errors for React or next/navigation, run:
// npm install --save-dev @types/react @types/node @types/next
// If you see JSX errors, ensure your tsconfig.json has "jsx": "react-jsx" or "react".

import React, { useEffect } from "react";
import { useSearchParams } from "next/navigation";

// Declare process and window as any to avoid linter errors if types are missing
// (for dev only; proper types should be installed in production)
declare const process: any;
declare const window: any;

export default function MicrosoftCallbackPage() {
  const searchParams = useSearchParams();

  useEffect(() => {
    const code = searchParams.get("code");
    const state = searchParams.get("state");

    if (code && state) {
      const apiBaseUrl =
        process?.env?.NEXT_PUBLIC_API_URL
          ? process.env.NEXT_PUBLIC_API_URL
          : (window?.location?.origin || "https://smartmeet-production.up.railway.app");
      window.location.href = `${apiBaseUrl}/connect/microsoft/callback?code=${encodeURIComponent(code)}&state=${encodeURIComponent(state)}`;
    }
    // Optionally, handle missing code/state here
  }, [searchParams]);

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div>
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <p>Redirecting to complete authentication...</p>
      </div>
    </div>
  );
}
