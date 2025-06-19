import * as React from "react";
import { useState, useEffect } from "react";

interface AvailabilityResult {
  meeting_id: string;
  proposed_times: Array<{
    start: string;
    end: string;
    confidence: number;
  }>;
  portal_url: string;
}

interface MeetingCreationResult {
  meeting_id: string;
  subject: string;
  start: string;
  end: string;
  web_link?: string;
  teams_link?: string;
  attendees: string[];
}

interface MeetingConfig {
  subject: string;
  duration: number;
  meetingType: "teams" | "in_person" | "phone";
  location: string;
  body: string;
  timeRange: number; // days to look ahead
}

const TaskPane: React.FC = () => {
  const [recipients, setRecipients] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AvailabilityResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [createdMeeting, setCreatedMeeting] =
    useState<MeetingCreationResult | null>(null);
  const [showConfig, setShowConfig] = useState(false);

  const [config, setConfig] = useState<MeetingConfig>({
    subject: "",
    duration: 30,
    meetingType: "teams",
    location: "",
    body: "",
    timeRange: 7,
  });

  const API_BASE_URL =
    process.env.NODE_ENV === "production"
      ? "https://smartmeet-production.up.railway.app"
      : "http://localhost:8000";

  useEffect(() => {
    // Initialize Office.js
    Office.onReady((info) => {
      if (info.host === Office.HostType.Outlook) {
        loadRecipients();
        checkAuthStatus();
      }
    });
  }, []);

  const checkAuthStatus = () => {
    // Check if we have a stored access token
    const token = localStorage.getItem("smartmeet_access_token");
    if (token) {
      setAccessToken(token);
      setIsAuthenticated(true);
    }
  };

  const authenticateWithMicrosoft = async () => {
    try {
      console.log("🚀 [ADDIN-DEBUG] Starting Microsoft authentication");
      setLoading(true);
      setError(null);

      // Get OAuth URL from backend
      console.log(
        "🔗 [ADDIN-DEBUG] Fetching OAuth URL from backend:",
        `${API_BASE_URL}/connect/microsoft/addin`
      );
      const response = await fetch(`${API_BASE_URL}/connect/microsoft/addin`);
      const data = await response.json();

      console.log("📦 [ADDIN-DEBUG] Backend response:", {
        status: response.status,
        ok: response.ok,
        hasAuthUrl: !!data.auth_url,
        state: data.state,
      });

      if (!data.auth_url) {
        console.error("❌ [ADDIN-DEBUG] No auth URL received from backend");
        throw new Error("Failed to get authentication URL");
      }

      console.log("🔍 [ADDIN-DEBUG] Full auth URL:", data.auth_url);

      // Use Office Dialog API instead of popup (much more reliable for add-ins)
      console.log("🖼️ [ADDIN-DEBUG] Opening Office dialog with auth URL");
      Office.context.ui.displayDialogAsync(
        data.auth_url,
        { height: 60, width: 60, displayInIframe: false },
        (dialogResult) => {
          console.log("📋 [ADDIN-DEBUG] Dialog open result:", {
            status: dialogResult.status,
            success: dialogResult.status === Office.AsyncResultStatus.Succeeded,
            error: dialogResult.error,
          });

          if (dialogResult.status === Office.AsyncResultStatus.Succeeded) {
            const dialog = dialogResult.value;
            console.log("✅ [ADDIN-DEBUG] Dialog opened successfully");

            // Listen for messages from the dialog (when OAuth completes)
            dialog.addEventHandler(
              Office.EventType.DialogMessageReceived,
              (messageEvent: any) => {
                console.log(
                  "💬 [ADDIN-DEBUG] Message received from dialog:",
                  messageEvent
                );
                try {
                  const message = JSON.parse(messageEvent.message);
                  console.log("📝 [ADDIN-DEBUG] Parsed message:", message);

                  if (message.type === "auth_success" && message.token) {
                    console.log("🎉 [ADDIN-DEBUG] Authentication successful!");
                    // Store the token and update auth state
                    setAccessToken(message.token);
                    setIsAuthenticated(true);
                    localStorage.setItem(
                      "smartmeet_access_token",
                      message.token
                    );
                    console.log("💾 [ADDIN-DEBUG] Token stored locally");
                  } else if (message.type === "auth_error") {
                    console.error(
                      "❌ [ADDIN-DEBUG] Authentication error from dialog:",
                      message.error
                    );
                    setError(message.error || "Authentication failed");
                  } else {
                    console.warn(
                      "⚠️ [ADDIN-DEBUG] Unexpected message type:",
                      message.type
                    );
                  }

                  console.log("🔐 [ADDIN-DEBUG] Closing dialog");
                  dialog.close();
                } catch (parseError) {
                  console.error(
                    "💥 [ADDIN-DEBUG] Error parsing dialog message:",
                    parseError
                  );
                  setError("Authentication communication error");
                  dialog.close();
                }
                setLoading(false);
              }
            );

            // Handle dialog navigation events (redirects, etc.)
            dialog.addEventHandler(
              Office.EventType.DialogEventReceived,
              (eventArgs: any) => {
                console.log(
                  "🚦 [ADDIN-DEBUG] Dialog event received:",
                  eventArgs
                );

                // Handle various dialog events
                if (eventArgs.error === 12006) {
                  // User closed dialog manually
                  console.log(
                    "👤 [ADDIN-DEBUG] User closed authentication dialog"
                  );
                  setLoading(false);
                } else if (eventArgs.error === 12002) {
                  // Dialog navigation error
                  console.error("🚫 [ADDIN-DEBUG] Dialog navigation error");
                  setError("Authentication navigation failed");
                  setLoading(false);
                } else {
                  console.log(
                    "ℹ️ [ADDIN-DEBUG] Other dialog event:",
                    eventArgs.error
                  );
                }
              }
            );
          } else {
            console.error(
              "💥 [ADDIN-DEBUG] Failed to open authentication dialog:",
              dialogResult.error
            );
            setError("Failed to open authentication dialog");
            setLoading(false);
          }
        }
      );
    } catch (err) {
      console.error("💥 [ADDIN-DEBUG] Authentication error:", err);
      setError("Failed to start authentication process");
      setLoading(false);
    }
  };

  const loadRecipients = async () => {
    try {
      if (Office.context.mailbox.item) {
        const item = Office.context.mailbox.item;
        const allEmails: string[] = [];

        // Get To recipients
        if (item.to && item.to.length > 0) {
          const toEmails = item.to.map((recipient) => recipient.emailAddress);
          allEmails.push(...toEmails);
        }

        // Also get CC recipients if available
        if (item.cc && item.cc.length > 0) {
          const ccEmails = item.cc.map((recipient) => recipient.emailAddress);
          allEmails.push(...ccEmails);
        }

        // Get subject for meeting title
        if (item.subject && !config.subject) {
          setConfig((prev) => ({
            ...prev,
            subject: `Meeting: ${item.subject}`,
          }));
        }

        setRecipients(allEmails);
      }
    } catch (err) {
      console.error("Error loading recipients:", err);
      setError("Failed to load recipients from email");
    }
  };

  const findMeetingTimes = async () => {
    if (!isAuthenticated) {
      setError("Please authenticate with Microsoft first");
      return;
    }

    if (recipients.length === 0) {
      setError("No recipients found. Please add recipients to your email.");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/availability`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${accessToken}`,
        },
        body: JSON.stringify({
          emails: recipients,
          start_time: new Date().toISOString(),
          end_time: new Date(
            Date.now() + config.timeRange * 24 * 60 * 60 * 1000
          ).toISOString(),
          duration_minutes: config.duration,
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to find meeting times");
      }

      const data: AvailabilityResult = await response.json();
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  const createMeeting = async (timeIndex: number) => {
    if (!isAuthenticated || !result) return;

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(
        `${API_BASE_URL}/meetings/create?selected_time_index=${timeIndex}`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${accessToken}`,
          },
          body: JSON.stringify({
            emails: recipients,
            subject: config.subject || "SmartMeet Scheduled Meeting",
            duration_minutes: config.duration,
            meeting_type: config.meetingType,
            location: config.location,
            body: config.body,
            time_zone: Intl.DateTimeFormat().resolvedOptions().timeZone,
          }),
        }
      );

      if (!response.ok) {
        throw new Error("Failed to create meeting");
      }

      const meetingData: MeetingCreationResult = await response.json();
      setCreatedMeeting(meetingData);

      // Optionally insert meeting details into email
      await insertMeetingDetails(meetingData);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create meeting");
    } finally {
      setLoading(false);
    }
  };

  const insertMeetingDetails = async (meeting: MeetingCreationResult) => {
    try {
      const meetingText = `
Meeting Created Successfully!

Subject: ${meeting.subject}
Date & Time: ${new Date(meeting.start).toLocaleString()} - ${new Date(
        meeting.end
      ).toLocaleString()}
${meeting.teams_link ? `Teams Link: ${meeting.teams_link}` : ""}
${meeting.web_link ? `Outlook Link: ${meeting.web_link}` : ""}

Attendees: ${meeting.attendees.join(", ")}

Meeting invites have been sent to all participants.
      `.trim();

      if (Office.context.mailbox.item && Office.context.mailbox.item.body) {
        Office.context.mailbox.item.body.setSelectedDataAsync(
          meetingText,
          { coercionType: Office.CoercionType.Text },
          (result) => {
            if (result.status === Office.AsyncResultStatus.Succeeded) {
              console.log("Meeting details inserted successfully");
            }
          }
        );
      }
    } catch (err) {
      console.error("Error inserting meeting details:", err);
    }
  };

  const formatTime = (dateStr: string) => {
    const date = new Date(dateStr);
    return {
      date: date.toLocaleDateString(),
      time: date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      dayOfWeek: date.toLocaleDateString([], { weekday: "long" }),
    };
  };

  const resetFlow = () => {
    setResult(null);
    setCreatedMeeting(null);
    setError(null);
  };

  if (createdMeeting) {
    return (
      <div className="taskpane-container">
        <header className="taskpane-header success">
          <div className="success-icon">✓</div>
          <h1>Meeting Created!</h1>
          <p>Your meeting has been scheduled successfully</p>
        </header>

        <div className="taskpane-content">
          <div className="meeting-summary">
            <h3>{createdMeeting.subject}</h3>
            <div className="meeting-details">
              <p>
                <strong>Date:</strong>{" "}
                {new Date(createdMeeting.start).toLocaleDateString()}
              </p>
              <p>
                <strong>Time:</strong>{" "}
                {new Date(createdMeeting.start).toLocaleTimeString()} -{" "}
                {new Date(createdMeeting.end).toLocaleTimeString()}
              </p>
              <p>
                <strong>Attendees:</strong> {createdMeeting.attendees.length}{" "}
                people
              </p>

              {createdMeeting.teams_link && (
                <div className="teams-link">
                  <p>
                    <strong>Teams Meeting:</strong>
                  </p>
                  <a
                    href={createdMeeting.teams_link}
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    Join Microsoft Teams Meeting
                  </a>
                </div>
              )}
            </div>
          </div>

          <div className="actions-section">
            <button className="primary-button" onClick={resetFlow}>
              Schedule Another Meeting
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <div className="taskpane-container">
        <header className="taskpane-header">
          <h1>SmartMeet</h1>
          <p>Automatically schedule meetings</p>
        </header>

        <div className="taskpane-content">
          <div className="auth-section">
            <div className="auth-icon">🔐</div>
            <h3>Connect Your Calendar</h3>
            <p>
              To automatically schedule meetings, SmartMeet needs access to your
              calendar.
            </p>

            <button
              className="primary-button auth-button"
              onClick={authenticateWithMicrosoft}
              disabled={loading}
            >
              {loading ? "Connecting..." : "Connect Microsoft Calendar"}
            </button>

            <div className="privacy-note">
              <small>
                We only access your free/busy information to find optimal
                meeting times. Your calendar details remain private.
              </small>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="taskpane-container">
      <header className="taskpane-header">
        <h1>SmartMeet</h1>
        <p>Automatically schedule meetings</p>
        <div className="auth-status">✓ Connected</div>
      </header>

      <div className="taskpane-content">
        {error && (
          <div className="error-message">
            <strong>Error:</strong> {error}
          </div>
        )}

        <div className="recipients-section">
          <h3>Recipients ({recipients.length})</h3>
          {recipients.length > 0 ? (
            <ul className="recipients-list">
              {recipients.map((email, index) => (
                <li key={index} className="recipient-item">
                  {email}
                </li>
              ))}
            </ul>
          ) : (
            <p className="no-recipients">
              No recipients found. Add recipients to your email first.
            </p>
          )}
        </div>

        <div className="config-section">
          <button
            className="config-toggle"
            onClick={() => setShowConfig(!showConfig)}
          >
            ⚙️ Meeting Settings {showConfig ? "▼" : "▶"}
          </button>

          {showConfig && (
            <div className="config-panel">
              <div className="config-row">
                <label>Meeting Subject:</label>
                <input
                  type="text"
                  value={config.subject}
                  onChange={(e) =>
                    setConfig((prev) => ({ ...prev, subject: e.target.value }))
                  }
                  placeholder="Enter meeting subject"
                />
              </div>

              <div className="config-row">
                <label>Duration:</label>
                <select
                  value={config.duration}
                  onChange={(e) =>
                    setConfig((prev) => ({
                      ...prev,
                      duration: parseInt(e.target.value),
                    }))
                  }
                >
                  <option value={15}>15 minutes</option>
                  <option value={30}>30 minutes</option>
                  <option value={60}>1 hour</option>
                  <option value={90}>1.5 hours</option>
                  <option value={120}>2 hours</option>
                </select>
              </div>

              <div className="config-row">
                <label>Meeting Type:</label>
                <select
                  value={config.meetingType}
                  onChange={(e) =>
                    setConfig((prev) => ({
                      ...prev,
                      meetingType: e.target.value as
                        | "teams"
                        | "in_person"
                        | "phone",
                    }))
                  }
                >
                  <option value="teams">Microsoft Teams</option>
                  <option value="in_person">In Person</option>
                  <option value="phone">Phone Call</option>
                </select>
              </div>

              {config.meetingType === "in_person" && (
                <div className="config-row">
                  <label>Location:</label>
                  <input
                    type="text"
                    value={config.location}
                    onChange={(e) =>
                      setConfig((prev) => ({
                        ...prev,
                        location: e.target.value,
                      }))
                    }
                    placeholder="Enter meeting location"
                  />
                </div>
              )}

              <div className="config-row">
                <label>Search Range:</label>
                <select
                  value={config.timeRange}
                  onChange={(e) =>
                    setConfig((prev) => ({
                      ...prev,
                      timeRange: parseInt(e.target.value),
                    }))
                  }
                >
                  <option value={3}>Next 3 days</option>
                  <option value={7}>Next week</option>
                  <option value={14}>Next 2 weeks</option>
                  <option value={30}>Next month</option>
                </select>
              </div>
            </div>
          )}
        </div>

        <div className="actions-section">
          <button
            className="primary-button"
            onClick={findMeetingTimes}
            disabled={loading || recipients.length === 0}
          >
            {loading ? "Finding Times..." : "Find Available Times"}
          </button>
        </div>

        {result && (
          <div className="results-section">
            <h3>Available Meeting Times</h3>
            <p className="results-subtitle">
              Click on a time to create the meeting automatically
            </p>

            <div className="meeting-times">
              {result.proposed_times.map((time, index) => {
                const timeInfo = formatTime(time.start);
                const endTime = formatTime(time.end);
                const confidence = Math.round(time.confidence * 100);

                return (
                  <div
                    key={index}
                    className={`meeting-time-card clickable confidence-${
                      confidence >= 90
                        ? "high"
                        : confidence >= 70
                        ? "medium"
                        : "low"
                    }`}
                    onClick={() => createMeeting(index)}
                  >
                    <div className="time-info">
                      <div className="day-info">
                        <strong>{timeInfo.dayOfWeek}</strong>
                        <span>{timeInfo.date}</span>
                      </div>
                      <div className="time-range">
                        {timeInfo.time} - {endTime.time}
                      </div>
                    </div>
                    <div className="confidence-badge">{confidence}% match</div>
                    <div className="create-button">📅 Create Meeting</div>
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default TaskPane;
