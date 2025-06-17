"use client";

import { useSearchParams, useRouter } from "next/navigation";
import { useEffect, useState, Suspense } from "react";

function CallbackContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const [status, setStatus] = useState<"processing" | "success" | "error">(
    "processing"
  );
  const [error, setError] = useState<string | null>(null);
  const [userToken, setUserToken] = useState<string | null>(null);

  const API_BASE_URL =
    process.env.NEXT_PUBLIC_API_URL ||
    "https://smartmeet-production.up.railway.app";

  useEffect(() => {
    const handleCallback = async () => {
      const code = searchParams.get("code");
      const state = searchParams.get("state");
      const errorParam = searchParams.get("error");

      if (errorParam) {
        setError(`OAuth error: ${errorParam}`);
        setStatus("error");
        return;
      }

      if (!code || !state) {
        setError("Missing authorization code or state parameter");
        setStatus("error");
        return;
      }

      try {
        // Forward the callback to your Railway backend
        console.log(
          `Making request to: ${API_BASE_URL}/connect/microsoft/callback?code=${code}&state=${state}`
        );

        const response = await fetch(
          `${API_BASE_URL}/connect/microsoft/callback?code=${code}&state=${state}`,
          {
            method: "GET",
            headers: {
              "Content-Type": "application/json",
            },
            mode: "cors", // Explicitly set CORS mode
          }
        );

        console.log("Response status:", response.status);
        console.log(
          "Response headers:",
          Object.fromEntries(response.headers.entries())
        );

        if (!response.ok) {
          const errorText = await response.text();
          console.error("Response error:", errorText);
          throw new Error(`Callback failed: ${response.status} - ${errorText}`);
        }

        // Check if it's a redirect response
        if (response.redirected || response.url.includes("/success")) {
          console.log("Detected redirect response, URL:", response.url);
          // Extract user_id from the redirect URL if present
          const url = new URL(response.url);
          const userId = url.searchParams.get("user_id");

          if (userId) {
            // For now, we'll store the user_id as a token placeholder
            // In a real implementation, you'd get the actual access token
            setUserToken(userId);
            localStorage.setItem("smartmeet_access_token", userId);
            console.log("Stored user token:", userId);
          }

          setStatus("success");
        } else {
          const data = await response.json();
          console.log("Response data:", data);
          if (data.access_token) {
            setUserToken(data.access_token);
            localStorage.setItem("smartmeet_access_token", data.access_token);
            setStatus("success");
          } else {
            throw new Error("No access token received");
          }
        }
      } catch (err) {
        console.error("Callback error:", err);
        console.error("Error details:", {
          name: err instanceof Error ? err.name : "Unknown",
          message:
            err instanceof Error ? err.message : "Unknown error occurred",
          stack: err instanceof Error ? err.stack : undefined,
        });
        setError(err instanceof Error ? err.message : "Unknown error occurred");
        setStatus("error");
      }
    };

    handleCallback();
  }, [searchParams, API_BASE_URL]);

  const closeWindow = () => {
    // Try to close the popup window
    if (window.opener) {
      window.close();
    } else {
      // If not in a popup, redirect to success page
      router.push("/success?provider=microsoft");
    }
  };

  if (status === "processing") {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
        <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8 text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <h1 className="text-xl font-semibold text-gray-900 mb-2">
            Connecting Your Calendar
          </h1>
          <p className="text-gray-600">
            Please wait while we complete the authentication process...
          </p>
        </div>
      </div>
    );
  }

  if (status === "error") {
    return (
      <div className="min-h-screen bg-gradient-to-br from-red-50 to-red-100 flex items-center justify-center p-4">
        <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8 text-center">
          <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg
              className="w-6 h-6 text-red-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </div>
          <h1 className="text-xl font-semibold text-gray-900 mb-2">
            Connection Failed
          </h1>
          <p className="text-gray-600 mb-4">
            {error || "Something went wrong during authentication"}
          </p>
          <div className="space-y-2">
            <button
              onClick={closeWindow}
              className="w-full px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 transition-colors"
            >
              Close Window
            </button>
            <button
              onClick={() => router.push("/connect")}
              className="w-full px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50 transition-colors"
            >
              Try Again
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Success state
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
        <p className="text-gray-600 mb-4">
          Your Microsoft calendar has been connected to SmartMeet.
        </p>

        {userToken && (
          <div className="mb-4 p-3 bg-gray-50 rounded-lg">
            <p className="text-xs text-gray-500 mb-1">Token ID:</p>
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
          <p className="text-xs text-gray-500">
            You can now use the SmartMeet add-in in Outlook
          </p>
        </div>
      </div>
    </div>
  );
}

export default function MicrosoftCallbackPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      }
    >
      <CallbackContent />
    </Suspense>
  );
}
