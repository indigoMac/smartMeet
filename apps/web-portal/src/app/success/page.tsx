"use client";

import { useSearchParams } from "next/navigation";
import { useEffect, useState, Suspense } from "react";

function SuccessPageContent() {
  const searchParams = useSearchParams();
  const [provider, setProvider] = useState<string | null>(null);
  const [userId, setUserId] = useState<string | null>(null);

  useEffect(() => {
    setProvider(searchParams.get("provider"));
    setUserId(searchParams.get("user_id"));
  }, [searchParams]);

  const getProviderName = (provider: string | null) => {
    switch (provider) {
      case "microsoft":
        return "Microsoft Outlook";
      case "google":
        return "Google Calendar";
      default:
        return "your calendar";
    }
  };

  const getProviderIcon = (provider: string | null) => {
    if (provider === "microsoft") {
      return (
        <svg className="w-8 h-8" viewBox="0 0 24 24" fill="currentColor">
          <path d="M11.5 2v8.5H3V2h8.5zm0 19.5V13H3v8.5h8.5zM21 2v8.5h-8.5V2H21zm0 19.5V13h-8.5v8.5H21z" />
        </svg>
      );
    } else if (provider === "google") {
      return (
        <svg className="w-8 h-8" viewBox="0 0 24 24" fill="currentColor">
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
      );
    }
    return (
      <div className="w-8 h-8 bg-green-500 rounded-full flex items-center justify-center">
        <svg
          className="w-5 h-5 text-white"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M5 13l4 4L19 7"
          />
        </svg>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8">
        <div className="text-center">
          {/* Success Icon */}
          <div className="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-green-100 mb-6">
            <svg
              className="h-8 w-8 text-green-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M5 13l4 4L19 7"
              />
            </svg>
          </div>

          {/* Title */}
          <h1 className="text-2xl font-bold text-gray-900 mb-4">
            Successfully Connected!
          </h1>

          {/* Provider Info */}
          {provider && (
            <div className="flex items-center justify-center space-x-3 mb-6">
              <div className="text-blue-600">{getProviderIcon(provider)}</div>
              <span className="text-lg text-gray-700">
                {getProviderName(provider)}
              </span>
            </div>
          )}

          {/* Success Message */}
          <p className="text-gray-600 mb-8">
            Your calendar has been successfully connected to SmartMeet. You can
            now use the Outlook add-in to find optimal meeting times.
          </p>

          {/* User ID Display (for debugging) */}
          {userId && (
            <div className="mb-6 p-3 bg-gray-50 rounded-lg">
              <p className="text-xs text-gray-500 mb-1">User ID:</p>
              <p className="text-sm font-mono text-gray-700 break-all">
                {userId}
              </p>
            </div>
          )}

          {/* Action Buttons */}
          <div className="space-y-3">
            <button
              onClick={() => window.close()}
              className="w-full px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
            >
              Close Window
            </button>
            <button
              onClick={() => (window.location.href = "/")}
              className="w-full px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 transition-colors"
            >
              Back to Home
            </button>
          </div>

          {/* Next Steps */}
          <div className="mt-8 text-left">
            <h3 className="text-sm font-semibold text-gray-900 mb-2">
              Next Steps:
            </h3>
            <ul className="text-xs text-gray-600 space-y-1">
              <li>• Open Microsoft Outlook</li>
              <li>• Install the SmartMeet add-in</li>
              <li>
                • Use &quot;Find Meeting Times&quot; when composing emails
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function SuccessPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading...</p>
          </div>
        </div>
      }
    >
      <SuccessPageContent />
    </Suspense>
  );
}
