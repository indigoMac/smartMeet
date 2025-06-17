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
      // Check for OAuth errors first
      const errorParam = searchParams.get("error");
      const errorDescription = searchParams.get("error_description");

      if (errorParam) {
        setError(
          `OAuth error: ${errorParam}${
            errorDescription ? ` - ${errorDescription}` : ""
          }`
        );
        setStatus("error");
        return;
      }

      // Check if we're already on a success redirect from the backend
      const provider = searchParams.get("provider");
      const userId = searchParams.get("user_id");

      if (provider === "microsoft" && userId) {
        // Success! The backend already handled the OAuth exchange
        console.log("OAuth success! User ID:", userId);
        setUserToken(userId);
        localStorage.setItem("smartmeet_access_token", userId);
        setStatus("success");
        return;
      }

      // Otherwise, we need to handle the authorization code from Azure
      const code = searchParams.get("code");
      const state = searchParams.get("state");

      if (!code || !state) {
        setError("Missing authorization code or state parameter");
        setStatus("error");
        return;
      }

      try {
        // Forward the callback to the Railway backend
        console.log(
          `Forwarding OAuth callback to: ${API_BASE_URL}/connect/microsoft/callback?code=${code}&state=${state}`
        );

        const response = await fetch(
          `${API_BASE_URL}/connect/microsoft/callback?code=${code}&state=${state}`,
          {
            method: "GET",
            redirect: "manual", // Don't automatically follow redirects
          }
        );

        console.log("Backend response status:", response.status);
        console.log(
          "Backend response headers:",
          Object.fromEntries(response.headers.entries())
        );

        // The backend will redirect to the success page
        if (response.status === 307 || response.status === 302) {
          const redirectLocation = response.headers.get("location");
          console.log("Redirect location:", redirectLocation);

          if (redirectLocation) {
            // Extract user_id from the redirect URL
            const url = new URL(redirectLocation);
            const redirectUserId = url.searchParams.get("user_id");

            if (redirectUserId) {
              setUserToken(redirectUserId);
              localStorage.setItem("smartmeet_access_token", redirectUserId);
              setStatus("success");
              return;
            }
          }
        }

        // Handle error responses
        let errorMessage = "OAuth callback failed";
        try {
          const responseText = await response.text();
          console.log("Backend response text:", responseText);

          if (responseText.trim()) {
            const data = JSON.parse(responseText);
            errorMessage = data.detail || data.message || errorMessage;
          } else {
            errorMessage = `Backend returned empty response with status ${response.status}`;
          }
        } catch (parseError) {
          console.error("Failed to parse backend response:", parseError);
          errorMessage = `Backend response parsing failed (status ${response.status})`;
        }

        setError(errorMessage);
        setStatus("error");
      } catch (err) {
        console.error("Callback error:", err);
        setError(err instanceof Error ? err.message : "Network error occurred");
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
      // If not in a popup, redirect to connect page
      router.push("/connect");
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
