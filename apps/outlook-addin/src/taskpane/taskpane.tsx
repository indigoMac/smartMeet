import * as React from "react";
import { useState, useEffect } from "react";

interface AuthState {
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

const TaskPane: React.FC = () => {
  console.log("🔄 TaskPane component rendering...");

  // Add immediate alert to see if component is loading
  React.useEffect(() => {
    console.log(
      "🎯 React component mounted! This means the add-in is loading."
    );
    console.log("🎯 React component mounted!");

    // More detailed debugging
    console.log("🔍 React version:", React.version);
    console.log("🔍 Component state initialized");
    console.log("🔍 Office object:", typeof Office);
    console.log("🔍 Document ready state:", document.readyState);

    // Test if we can access DOM
    const rootElement = document.getElementById("root");
    console.log("🔍 Root element found:", !!rootElement);
  }, []);

  const [officeReady, setOfficeReady] = useState<boolean>(false);
  const [authState, setAuthState] = useState<AuthState>({
    isAuthenticated: false,
    isLoading: false,
    error: null,
  });
  const [statusMessage, setStatusMessage] = useState<string>("");

  useEffect(() => {
    console.log("🔄 TaskPane useEffect running...");
    console.log("📊 Office object available:", typeof Office !== "undefined");

    if (typeof Office !== "undefined") {
      console.log("🔄 Calling Office.onReady...");
      Office.onReady(() => {
        console.log("✅ Office.js is ready");
        setOfficeReady(true);
        checkExistingAuth();
      });
    } else {
      console.log("❌ Office object not available");
    }
  }, []);

  const checkExistingAuth = () => {
    console.log("🔍 Checking existing auth...");
    const existingToken = localStorage.getItem("smartmeet_access_token");
    console.log("🎫 Existing token:", existingToken ? "Found" : "Not found");
    if (existingToken) {
      setAuthState((prev) => ({
        ...prev,
        isAuthenticated: true,
      }));
    }
  };

  const handleConnectCalendar = async () => {
    console.log("🔗 CONNECT BUTTON CLICKED! Starting authentication...");
    console.log("🚀 Connect to Calendar button clicked!");
    console.log("📊 Office ready status:", officeReady);
    console.log("📊 Current auth state:", authState);
    console.log("🔍 Office object type:", typeof Office);
    console.log("🔍 Office.context available:", typeof Office?.context);

    if (!officeReady) {
      console.log("❌ Office.js not ready");
      console.log("🔧 Attempting to proceed anyway for API testing...");
      // Don't return here - let's test the API anyway
      // setAuthState((prev) => ({ ...prev, error: "Office.js not ready" }));
      // return;
    }

    console.log("⏳ Starting authentication flow...");
    setAuthState((prev) => ({ ...prev, isLoading: true, error: null }));

    try {
      const API_BASE_URL =
        process.env.NODE_ENV === "production"
          ? "https://smartmeet-production.up.railway.app"
          : "http://localhost:8000";

      console.log("🌐 API Base URL:", API_BASE_URL);
      console.log("📞 Making request to:", `${API_BASE_URL}/connect/microsoft`);

      const response = await fetch(`${API_BASE_URL}/connect/microsoft`);
      console.log("📡 Response status:", response.status);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      console.log("📄 Response data:", data);
      console.log(`📄 Got auth URL: ${data.auth_url ? "✅ Yes" : "❌ No"}`);

      if (!data.auth_url) {
        throw new Error("Failed to get authorization URL");
      }

      console.log("🔗 Opening OAuth dialog with URL:", data.auth_url);
      console.log("🔗 About to open OAuth dialog...");

      Office.context.ui.displayDialogAsync(
        data.auth_url,
        { height: 60, width: 60 },
        (result) => {
          console.log("🗂️ Dialog result status:", result.status);
          console.log("🗂️ Dialog result:", result);

          if (result.status === Office.AsyncResultStatus.Succeeded) {
            console.log("✅ Dialog opened successfully");
            const dialog = result.value;

            dialog.addEventHandler(
              Office.EventType.DialogMessageReceived,
              (arg) => {
                console.log("📨 Message received from dialog:", arg);
                if ("message" in arg) {
                  try {
                    const message = JSON.parse(arg.message);
                    console.log("📋 Parsed message:", message);

                    if (message.type === "auth_success") {
                      console.log("🎉 Authentication successful!");
                      localStorage.setItem(
                        "smartmeet_access_token",
                        message.access_token || "connected"
                      );
                      setAuthState({
                        isAuthenticated: true,
                        isLoading: false,
                        error: null,
                      });
                      dialog.close();
                    } else if (message.type === "auth_error") {
                      console.log("❌ Authentication error:", message.error);
                      setAuthState((prev) => ({
                        ...prev,
                        isLoading: false,
                        error: message.error,
                      }));
                      dialog.close();
                    }
                  } catch (parseError) {
                    console.log("❌ Parse error:", parseError);
                    setAuthState((prev) => ({
                      ...prev,
                      isLoading: false,
                      error: "Failed to process authentication response",
                    }));
                    dialog.close();
                  }
                }
              }
            );

            dialog.addEventHandler(
              Office.EventType.DialogEventReceived,
              (arg) => {
                console.log("🗂️ Dialog event received:", arg);
                if ("error" in arg && arg.error === 12006) {
                  console.log("❌ Dialog closed by user");
                  setAuthState((prev) => ({ ...prev, isLoading: false }));
                }
              }
            );
          } else {
            console.log("❌ Failed to open dialog:", result.error);
            setAuthState((prev) => ({
              ...prev,
              isLoading: false,
              error: `Failed to open authentication dialog: ${
                result.error?.message || "Unknown error"
              }`,
            }));
          }
        }
      );
    } catch (error) {
      console.log("❌ Error in handleConnectCalendar:", error);
      setAuthState((prev) => ({
        ...prev,
        isLoading: false,
        error: error instanceof Error ? error.message : "Authentication failed",
      }));
    }
  };

  const handleDisconnect = () => {
    localStorage.removeItem("smartmeet_access_token");
    setAuthState({
      isAuthenticated: false,
      isLoading: false,
      error: null,
    });
  };

  // Test function to see if click events work
  const handleTestClick = () => {
    console.log("🚀 handleTestClick function called!");
    try {
      alert("🧪 TEST CLICK DETECTED! Buttons are working!");
      console.log("✅ Alert showed successfully");
    } catch (error) {
      console.log("❌ Alert failed:", error);
    }
    console.log("🧪 Test button clicked!");
    console.log("✅ Test button works! Click events are functioning.");
    console.log("🔍 Current timestamp:", new Date().toISOString());
    console.log("🔍 Event handler called successfully");
    try {
      setStatusMessage(
        "✅ Test button clicked! React and click events are working."
      );
      console.log("✅ setStatusMessage called successfully");
    } catch (error) {
      console.log("❌ setStatusMessage failed:", error);
    }
    setTimeout(() => {
      try {
        setStatusMessage("");
        console.log("✅ Cleared status message");
      } catch (error) {
        console.log("❌ Clear status message failed:", error);
      }
    }, 3000);
  };

  // Also add a ref to check if button renders
  const testButtonRef = React.useRef<HTMLButtonElement>(null);
  const yellowBoxRef = React.useRef<HTMLDivElement>(null);
  const connectButtonRef = React.useRef<HTMLButtonElement>(null);

  React.useEffect(() => {
    console.log("🔍 Test button ref:", testButtonRef.current);
    if (testButtonRef.current) {
      console.log("🔍 Test button element found in DOM");
      // Add event listener directly as backup
      const button = testButtonRef.current;
      const directClickHandler = () => {
        console.log("🔥 Direct event listener fired!");
        handleTestClick();
      };
      button.addEventListener("click", directClickHandler);

      return () => {
        button.removeEventListener("click", directClickHandler);
      };
    } else {
      console.log("❌ Test button ref is null - button not found in DOM");
    }
  }, []);

  React.useEffect(() => {
    console.log("🔍 Connect button ref:", connectButtonRef.current);
    if (connectButtonRef.current) {
      console.log("🔍 Connect button element found in DOM");
      // Add event listener directly as backup
      const button = connectButtonRef.current;
      const directClickHandler = () => {
        console.log("🔥 Connect button direct event listener fired!");
        handleConnectCalendar();
      };
      button.addEventListener("click", directClickHandler);

      return () => {
        button.removeEventListener("click", directClickHandler);
      };
    } else {
      console.log("❌ Connect button ref is null - button not found in DOM");
    }
  }, []);

  React.useEffect(() => {
    console.log("🔍 Yellow box ref:", yellowBoxRef.current);
    if (yellowBoxRef.current) {
      console.log("🔍 Yellow box element found in DOM");
      const box = yellowBoxRef.current;
      const directClickHandler = () => {
        console.log("🟡 Yellow box direct event listener fired!");
        alert("Yellow box clicked via direct listener!");
      };
      box.addEventListener("click", directClickHandler);

      return () => {
        box.removeEventListener("click", directClickHandler);
      };
    } else {
      console.log("❌ Yellow box ref is null - box not found in DOM");
    }
  }, []);

  if (!officeReady) {
    return (
      <div style={{ padding: "20px", textAlign: "center" }}>
        <div style={{ marginBottom: "20px" }}>⏳</div>
        <p>Initializing SmartMeet...</p>
      </div>
    );
  }

  return (
    <div
      style={{ padding: "20px", fontFamily: "'Segoe UI', Arial, sans-serif" }}
    >
      <div style={{ textAlign: "center", marginBottom: "30px" }}>
        <h1
          style={{ color: "#0078d4", margin: "0 0 10px 0", fontSize: "24px" }}
        >
          SmartMeet
        </h1>
        <p style={{ color: "#666", margin: "0", fontSize: "14px" }}>
          Calendar Integration
        </p>
      </div>

      {/* Status message display */}
      {statusMessage && (
        <div
          style={{
            background: "#d4edda",
            color: "#155724",
            padding: "10px",
            borderRadius: "4px",
            marginBottom: "20px",
            fontSize: "14px",
            textAlign: "center",
            border: "1px solid #c3e6cb",
          }}
        >
          {statusMessage}
        </div>
      )}

      {!authState.isAuthenticated ? (
        <div style={{ marginBottom: "30px" }}>
          <div
            style={{
              background: "#f8f9fa",
              padding: "20px",
              borderRadius: "8px",
              border: "1px solid #e9ecef",
              textAlign: "center",
            }}
          >
            <div style={{ fontSize: "48px", marginBottom: "15px" }}>📅</div>
            <h3 style={{ margin: "0 0 10px 0", color: "#333" }}>
              Connect Your Calendar
            </h3>
            <p
              style={{ color: "#666", fontSize: "14px", marginBottom: "20px" }}
            >
              Connect your Microsoft calendar to enable SmartMeet features.
            </p>

            <button
              ref={connectButtonRef}
              onClick={handleConnectCalendar}
              disabled={authState.isLoading}
              style={{
                background: authState.isLoading ? "#ccc" : "#0078d4",
                color: "white",
                padding: "12px 24px",
                border: "none",
                borderRadius: "6px",
                cursor: authState.isLoading ? "not-allowed" : "pointer",
                fontSize: "14px",
                fontWeight: "600",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                margin: "0 auto",
                minWidth: "200px",
              }}
              onMouseDown={() => console.log("🖱️ Connect button mouse down")}
              onMouseUp={() => console.log("🖱️ Connect button mouse up")}
            >
              {authState.isLoading ? (
                <>⏳ Connecting...</>
              ) : (
                <>
                  <span style={{ marginRight: "8px" }}>🔗</span>
                  Connect to Calendar
                </>
              )}
            </button>

            {/* Test button for debugging */}
            <button
              ref={testButtonRef}
              onClick={handleTestClick}
              style={{
                background: "#28a745",
                color: "white",
                padding: "8px 16px",
                border: "none",
                borderRadius: "4px",
                cursor: "pointer",
                fontSize: "12px",
                margin: "10px auto 0",
                display: "block",
              }}
              onMouseDown={() => console.log("🖱️ Test button mouse down")}
              onMouseUp={() => console.log("🖱️ Test button mouse up")}
            >
              🧪 Test Click
            </button>

            {/* Simple debugging div to test if ANY clicks work */}
            <div
              ref={yellowBoxRef}
              onClick={() => {
                console.log("🟢 SIMPLE DIV CLICKED!");
                alert("Simple div clicked - basic clicks work!");
              }}
              style={{
                background: "#ffc107",
                color: "#000",
                padding: "10px",
                margin: "10px auto",
                textAlign: "center",
                cursor: "pointer",
                border: "2px solid #000",
                borderRadius: "4px",
                maxWidth: "200px",
              }}
            >
              🟡 Click This Yellow Box
            </div>

            {authState.error && (
              <div
                style={{
                  background: "#f8d7da",
                  color: "#721c24",
                  padding: "10px",
                  borderRadius: "4px",
                  marginTop: "15px",
                  fontSize: "14px",
                }}
              >
                ❌ {authState.error}
              </div>
            )}
          </div>
        </div>
      ) : (
        <div style={{ marginBottom: "30px" }}>
          <div
            style={{
              background: "#d4edda",
              padding: "20px",
              borderRadius: "8px",
              border: "1px solid #c3e6cb",
              textAlign: "center",
              marginBottom: "20px",
            }}
          >
            <div style={{ fontSize: "32px", marginBottom: "10px" }}>✅</div>
            <h3 style={{ margin: "0 0 5px 0", color: "#155724" }}>
              Calendar Connected!
            </h3>
            <p style={{ color: "#155724", fontSize: "14px", margin: "0" }}>
              Your Microsoft calendar is connected and ready.
            </p>
          </div>

          <button
            onClick={handleDisconnect}
            style={{
              background: "#dc3545",
              color: "white",
              padding: "10px 15px",
              border: "none",
              borderRadius: "4px",
              cursor: "pointer",
              fontSize: "14px",
              width: "100%",
            }}
          >
            🔓 Disconnect Calendar
          </button>
        </div>
      )}
    </div>
  );
};

export default TaskPane;
