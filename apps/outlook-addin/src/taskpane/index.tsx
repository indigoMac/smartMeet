import * as React from "react";
import * as ReactDOM from "react-dom";
import TaskPane from "./taskpane";

// Enhanced error boundary for cross-origin errors
class ErrorBoundary extends React.Component<
  { children: React.ReactNode },
  { hasError: boolean; error?: Error }
> {
  constructor(props: { children: React.ReactNode }) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error) {
    console.error("React Error Boundary caught error:", error);
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: any) {
    console.error("React Error Boundary - Error Info:", errorInfo);

    // Handle cross-origin errors specifically
    if (error.message === "Script error." || error.message === "") {
      console.warn(
        "🌐 [ADDIN-DEBUG] Cross-origin script error caught (expected in add-in environment)"
      );
    }
  }

  render() {
    if (this.state.hasError) {
      return (
        <div
          style={{
            padding: "20px",
            color: "#721c24",
            background: "#f8d7da",
            border: "1px solid #f5c6cb",
            borderRadius: "4px",
          }}
        >
          <h2>🛠️ Development Error</h2>
          <p>
            <strong>Error:</strong>{" "}
            {this.state.error?.message || "Unknown error"}
          </p>
          <p style={{ fontSize: "14px", marginTop: "10px" }}>
            This is expected in development mode. The add-in should still
            function.
          </p>
          <button
            onClick={() => this.setState({ hasError: false })}
            style={{
              background: "#0078d4",
              color: "white",
              padding: "8px 16px",
              border: "none",
              borderRadius: "4px",
              cursor: "pointer",
              marginTop: "10px",
            }}
          >
            Retry
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

console.log("🚀 [ADDIN-DEBUG] Starting React app initialization");

// Handle global errors (including cross-origin)
window.addEventListener("error", (event) => {
  if (event.message === "Script error." && event.filename === "") {
    console.warn(
      "🌐 [ADDIN-DEBUG] Cross-origin script error caught (expected in add-in environment)"
    );
    event.preventDefault(); // Prevent the error from being logged to console
    return false;
  }
});

// Handle unhandled promise rejections
window.addEventListener("unhandledrejection", (event) => {
  console.warn("🚨 [ADDIN-DEBUG] Unhandled promise rejection:", event.reason);
  // Don't prevent default for debugging purposes
});

// Wait for DOM to be ready
const initializeApp = () => {
  console.log("🎯 [ADDIN-DEBUG] DOM ready, looking for root element");
  const container = document.getElementById("root");

  if (container) {
    console.log("✅ [ADDIN-DEBUG] Root element found, rendering React app");
    ReactDOM.render(
      <ErrorBoundary>
        <TaskPane />
      </ErrorBoundary>,
      container
    );
    console.log("🎉 [ADDIN-DEBUG] React app rendered successfully");
  } else {
    console.error("❌ [ADDIN-DEBUG] Root element not found!");
    // Retry after a short delay
    setTimeout(initializeApp, 100);
  }
};

// Initialize when DOM is ready
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initializeApp);
} else {
  initializeApp();
}
