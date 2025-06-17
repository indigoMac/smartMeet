"use client";

import { useSearchParams, useRouter } from "next/navigation";
import { useEffect, useState, Suspense } from "react";

function SuccessContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const [userToken, setUserToken] = useState<string | null>(null);

  useEffect(() => {
    const provider = searchParams.get("provider");
    const userId = searchParams.get("user_id");

    if (provider && userId) {
      // Store the user ID as our token
      setUserToken(userId);
      localStorage.setItem("smartmeet_access_token", userId);
    }
  }, [searchParams]);

  const closeWindow = () => {
    // Try to close the popup window
    if (window.opener) {
      window.close();
    } else {
      // If not in a popup, redirect to connect page
      router.push("/connect");
    }
  };

  const provider = searchParams.get("provider");
  const providerName =
    provider === "microsoft"
      ? "Microsoft Outlook"
      : provider === "google"
      ? "Google Calendar"
      : "Calendar";

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-green-100 flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8 text-center">
        <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <svg
            className="w-6 h-6 text-green-600"
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

        <h1 className="text-xl font-semibold text-gray-900 mb-2">
          Successfully Connected!
        </h1>

        <div className="flex items-center justify-center mb-4">
          {provider === "microsoft" && (
            <div className="w-8 h-8 bg-blue-600 rounded flex items-center justify-center mr-2">
              <span className="text-white text-xs font-bold">M</span>
            </div>
          )}
          {provider === "google" && (
            <div className="w-8 h-8 bg-red-500 rounded flex items-center justify-center mr-2">
              <span className="text-white text-xs font-bold">G</span>
            </div>
          )}
          <span className="text-gray-700">{providerName}</span>
        </div>

        <p className="text-gray-600 mb-4">
          Your calendar has been successfully connected to SmartMeet. You can
          now use the Outlook add-in to find optimal meeting times.
        </p>

        {userToken && (
          <div className="mb-4 p-3 bg-gray-50 rounded-lg">
            <p className="text-xs text-gray-500 mb-1">Connection ID:</p>
            <p className="text-sm font-mono text-gray-700 break-all">
              {userToken.substring(0, 20)}...
            </p>
          </div>
        )}

        <div className="space-y-2">
          <button
            onClick={closeWindow}
            className="w-full px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
          >
            Close Window
          </button>

          <div className="mt-4 p-3 bg-blue-50 rounded-lg text-left">
            <h3 className="font-semibold text-gray-900 mb-2">Next Steps:</h3>
            <ul className="text-sm text-gray-700 space-y-1">
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
        <div className="min-h-screen bg-gradient-to-br from-green-50 to-green-100 flex items-center justify-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600"></div>
        </div>
      }
    >
      <SuccessContent />
    </Suspense>
  );
}
