"use client";

import { useState } from "react";

export default function ConnectPage() {
  const [loading, setLoading] = useState<string | null>(null);

  const API_BASE_URL =
    process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  const handleConnect = async (provider: "microsoft" | "google") => {
    setLoading(provider);

    try {
      const response = await fetch(`${API_BASE_URL}/connect/${provider}`);
      const data = await response.json();

      if (data.auth_url) {
        window.location.href = data.auth_url;
      } else {
        throw new Error("No auth URL received");
      }
    } catch (error) {
      console.error("Failed to start OAuth flow:", error);
      setLoading(null);
      alert("Failed to connect. Please try again.");
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">SmartMeet</h1>
          <p className="text-gray-600">
            Connect your calendar to find the best meeting times
          </p>
        </div>

        <div className="space-y-4">
          <button
            onClick={() => handleConnect("microsoft")}
            disabled={loading === "microsoft"}
            className="w-full flex items-center justify-center px-4 py-3 border border-transparent rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading === "microsoft" ? (
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
            ) : (
              <>
                <svg
                  className="w-5 h-5 mr-2"
                  viewBox="0 0 24 24"
                  fill="currentColor"
                >
                  <path d="M11.5 2v8.5H3V2h8.5zm0 19.5V13H3v8.5h8.5zM21 2v8.5h-8.5V2H21zm0 19.5V13h-8.5v8.5H21z" />
                </svg>
                Connect Microsoft Outlook
              </>
            )}
          </button>

          <button
            onClick={() => handleConnect("google")}
            disabled={loading === "google"}
            className="w-full flex items-center justify-center px-4 py-3 border border-gray-300 rounded-md shadow-sm text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading === "google" ? (
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-gray-600"></div>
            ) : (
              <>
                <svg
                  className="w-5 h-5 mr-2"
                  viewBox="0 0 24 24"
                  fill="currentColor"
                >
                  <path
                    d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
                    fill="#4285F4"
                  />
                  <path
                    d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
                    fill="#34A853"
                  />
                  <path
                    d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
                    fill="#FBBC05"
                  />
                  <path
                    d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
                    fill="#EA4335"
                  />
                </svg>
                Connect Google Calendar
              </>
            )}
          </button>
        </div>

        <div className="mt-8 text-center">
          <p className="text-sm text-gray-500">
            We only access your free/busy information to find optimal meeting
            times. Your calendar details remain private.
          </p>
        </div>
      </div>
    </div>
  );
}
