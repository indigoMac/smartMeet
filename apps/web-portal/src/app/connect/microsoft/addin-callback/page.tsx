"use client";

import { useSearchParams } from "next/navigation";
import { useEffect, useState, Suspense } from "react";

// TypeScript declaration for Office API
declare global {
  interface Window {
    Office?: {
      context?: {
        ui?: {
          messageParent: (message: string) => void;
        };
      };
    };
  }
}

const AddinCallbackContent = () => {
  const searchParams = useSearchParams();
  const [status, setStatus] = useState<"processing" | "success" | "error">(
    "processing"
  );
  const [errorMessage, setErrorMessage] = useState<string>("");

  useEffect(() => {
    const handleCallback = async () => {
      console.log("🚀 [CALLBACK-DEBUG] Starting add-in OAuth callback process");

      try {
        // Get parameters from URL
        const code = searchParams.get("code");
        const state = searchParams.get("state");
        const error = searchParams.get("error");
        const errorDescription = searchParams.get("error_description");

        console.log("📝 [CALLBACK-DEBUG] URL params:", {
          code: code ? `${code.substring(0, 20)}...` : null,
          state,
          error,
          errorDescription,
          fullUrl: window.location.href,
        });

        // Handle OAuth errors
        if (error) {
          const message = `OAuth error: ${error}${
            errorDescription ? ` - ${errorDescription}` : ""
          }`;
          console.error("❌ [CALLBACK-DEBUG] OAuth error received:", message);
          setErrorMessage(message);
          setStatus("error");

          // Send error message to Office dialog parent
          if (typeof window !== "undefined" && window.Office?.context?.ui) {
            console.log("📤 [CALLBACK-DEBUG] Sending error to Office dialog");
            window.Office.context.ui.messageParent(
              JSON.stringify({
                type: "auth_error",
                error: message,
              })
            );
          } else {
            console.warn(
              "⚠️ [CALLBACK-DEBUG] Office API not available for error messaging"
            );
          }
          return;
        }

        // Validate required parameters
        if (!code) {
          const message = "Authorization code not received";
          console.error("❌ [CALLBACK-DEBUG] Missing authorization code");
          setErrorMessage(message);
          setStatus("error");

          if (typeof window !== "undefined" && window.Office?.context?.ui) {
            console.log(
              "📤 [CALLBACK-DEBUG] Sending 'no code' error to Office dialog"
            );
            window.Office.context.ui.messageParent(
              JSON.stringify({
                type: "auth_error",
                error: message,
              })
            );
          } else {
            console.warn(
              "⚠️ [CALLBACK-DEBUG] Office API not available for error messaging"
            );
          }
          return;
        }

        // Exchange code for token via backend
        const API_BASE_URL =
          process.env.NEXT_PUBLIC_API_URL ||
          "https://smartmeet-production.up.railway.app";

        console.log("🔗 [CALLBACK-DEBUG] Making request to backend:", {
          url: `${API_BASE_URL}/connect/microsoft/callback`,
          method: "POST",
          redirectUri: window.location.origin + window.location.pathname,
        });

        const response = await fetch(
          `${API_BASE_URL}/connect/microsoft/callback`,
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({
              code,
              state,
              redirect_uri: window.location.origin + window.location.pathname,
            }),
          }
        );

        console.log("📊 [CALLBACK-DEBUG] Backend response:", {
          status: response.status,
          statusText: response.statusText,
          ok: response.ok,
        });

        const data = await response.json();
        console.log("📦 [CALLBACK-DEBUG] Backend response data:", {
          success: data.success,
          hasAccessToken: !!data.access_token,
          hasUserId: !!data.user_id,
          message: data.message,
          error: data.detail || data.error,
        });

        if (!response.ok) {
          throw new Error(
            data.detail || data.message || "Failed to complete authentication"
          );
        }

        // Success! Send token to parent Office dialog
        console.log(
          "✅ [CALLBACK-DEBUG] Authentication successful, sending to Office dialog"
        );
        setStatus("success");

        if (typeof window !== "undefined" && window.Office?.context?.ui) {
          const messagePayload = {
            type: "auth_success",
            token: data.access_token || data.token || "authenticated",
            user_id: data.user_id,
          };
          console.log(
            "📤 [CALLBACK-DEBUG] Sending success message to Office:",
            messagePayload
          );

          window.Office.context.ui.messageParent(
            JSON.stringify(messagePayload)
          );
        } else {
          // Fallback for testing outside Office
          console.log(
            "⚠️ [CALLBACK-DEBUG] Office API not available, logging success locally:",
            data
          );
        }
      } catch (error) {
        console.error("💥 [CALLBACK-DEBUG] Callback error:", error);
        const message =
          error instanceof Error ? error.message : "Unknown error occurred";
        setErrorMessage(message);
        setStatus("error");

        if (typeof window !== "undefined" && window.Office?.context?.ui) {
          console.log(
            "📤 [CALLBACK-DEBUG] Sending exception error to Office dialog"
          );
          window.Office.context.ui.messageParent(
            JSON.stringify({
              type: "auth_error",
              error: message,
            })
          );
        } else {
          console.warn(
            "⚠️ [CALLBACK-DEBUG] Office API not available for exception error messaging"
          );
        }
      }
    };

    handleCallback();
  }, [searchParams]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full bg-white rounded-lg shadow-md p-6">
        {status === "processing" && (
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <h2 className="text-xl font-semibold text-gray-900 mb-2">
              Connecting Calendar
            </h2>
            <p className="text-gray-600">
              Please wait while we complete the connection...
            </p>
          </div>
        )}

        {status === "error" && (
          <div className="text-center">
            <div className="text-red-500 text-5xl mb-4">⚠️</div>
            <h2 className="text-xl font-semibold text-gray-900 mb-2">
              Connection Failed
            </h2>
            <p className="text-gray-600 mb-4">{errorMessage}</p>
            <div className="text-sm text-gray-500">
              This window will close automatically. Please try again from the
              add-in.
            </div>
          </div>
        )}

        {status === "success" && (
          <div className="text-center">
            <div className="text-green-500 text-5xl mb-4">✅</div>
            <h2 className="text-xl font-semibold text-gray-900 mb-2">
              Calendar Connected!
            </h2>
            <p className="text-gray-600 mb-4">
              Your Microsoft calendar has been successfully connected.
            </p>
            <div className="text-sm text-gray-500">
              This window will close automatically. You can now use SmartMeet
              features in Outlook.
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

const LoadingFallback = () => (
  <div className="min-h-screen flex items-center justify-center bg-gray-50">
    <div className="max-w-md w-full bg-white rounded-lg shadow-md p-6">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <h2 className="text-xl font-semibold text-gray-900 mb-2">Loading...</h2>
        <p className="text-gray-600">Initializing authentication...</p>
      </div>
    </div>
  </div>
);

export default function AddinCallbackPage() {
  return (
    <Suspense fallback={<LoadingFallback />}>
      <AddinCallbackContent />
    </Suspense>
  );
}
