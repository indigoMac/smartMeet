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

const TaskPane: React.FC = () => {
  const [recipients, setRecipients] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AvailabilityResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const API_BASE_URL =
    process.env.NODE_ENV === "production"
      ? "https://smartmeet-production.up.railway.app"
      : "http://localhost:8000";

  useEffect(() => {
    // Initialize Office.js
    Office.onReady((info) => {
      if (info.host === Office.HostType.Outlook) {
        loadRecipients();
      }
    });
  }, []);

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

        setRecipients(allEmails);
      }
    } catch (err) {
      console.error("Error loading recipients:", err);
      setError("Failed to load recipients from email");
    }
  };

  const findMeetingTimes = async () => {
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
        },
        body: JSON.stringify({
          emails: recipients,
          start_time: new Date().toISOString(),
          end_time: new Date(
            Date.now() + 7 * 24 * 60 * 60 * 1000
          ).toISOString(), // Next 7 days
          duration_minutes: 30,
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

  const insertMeetingTimes = async () => {
    if (!result) return;

    try {
      const meetingTimesText = result.proposed_times
        .map((time, index) => {
          const start = new Date(time.start);
          const end = new Date(time.end);
          const confidence = Math.round(time.confidence * 100);

          return `${
            index + 1
          }. ${start.toLocaleDateString()} ${start.toLocaleTimeString()} - ${end.toLocaleTimeString()} (${confidence}% confidence)`;
        })
        .join("\n");

      const fullText = `SmartMeet has found the following optimal meeting times:\n\n${meetingTimesText}\n\nParticipants can view and select their preferred time at: ${result.portal_url}`;

      if (Office.context.mailbox.item && Office.context.mailbox.item.body) {
        Office.context.mailbox.item.body.setSelectedDataAsync(
          fullText,
          { coercionType: Office.CoercionType.Text },
          (result) => {
            if (result.status === Office.AsyncResultStatus.Succeeded) {
              console.log("Meeting times inserted successfully");
            } else {
              console.error("Failed to insert meeting times:", result.error);
            }
          }
        );
      }
    } catch (err) {
      console.error("Error inserting meeting times:", err);
      setError("Failed to insert meeting times into email");
    }
  };

  const formatTime = (dateStr: string) => {
    const date = new Date(dateStr);
    return {
      date: date.toLocaleDateString(),
      time: date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    };
  };

  return (
    <div className="taskpane-container">
      <header className="taskpane-header">
        <h1>SmartMeet</h1>
        <p>Find optimal meeting times</p>
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

        <div className="actions-section">
          <button
            className="primary-button"
            onClick={findMeetingTimes}
            disabled={loading || recipients.length === 0}
          >
            {loading ? "Finding Times..." : "Find Meeting Times"}
          </button>

          <button
            className="secondary-button"
            onClick={loadRecipients}
            disabled={loading}
          >
            Refresh Recipients
          </button>
        </div>

        {result && (
          <div className="results-section">
            <h3>Proposed Meeting Times</h3>
            <div className="meeting-times">
              {result.proposed_times.map((time, index) => {
                const start = formatTime(time.start);
                const end = formatTime(time.end);
                const confidence = Math.round(time.confidence * 100);

                return (
                  <div key={index} className="meeting-time-card">
                    <div className="time-info">
                      <strong>{start.date}</strong>
                      <span>
                        {start.time} - {end.time}
                      </span>
                    </div>
                    <div
                      className={`confidence confidence-${
                        confidence >= 90
                          ? "high"
                          : confidence >= 70
                          ? "medium"
                          : "low"
                      }`}
                    >
                      {confidence}% confidence
                    </div>
                  </div>
                );
              })}
            </div>

            <div className="portal-link">
              <p>
                <strong>Share with participants:</strong>
              </p>
              <code className="portal-url">{result.portal_url}</code>
            </div>

            <button className="primary-button" onClick={insertMeetingTimes}>
              Insert Times into Email
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default TaskPane;
