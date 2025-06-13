"use client";

import { useState, useEffect } from "react";
import { useParams } from "next/navigation";

interface ProposedTime {
  start: string;
  end: string;
  confidence: number;
}

interface MeetingData {
  meeting_id: string;
  emails: string[];
  proposed_times: ProposedTime[];
  created_at: string;
}

export default function AvailabilityPage() {
  const params = useParams();
  const meetingId = params.meetingId as string;
  const [meetingData, setMeetingData] = useState<MeetingData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedTime, setSelectedTime] = useState<number | null>(null);

  const API_BASE_URL =
    process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

  useEffect(() => {
    if (meetingId) {
      fetchMeetingData();
    }
  }, [meetingId]);

  const fetchMeetingData = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_BASE_URL}/availability/${meetingId}`);

      if (!response.ok) {
        throw new Error("Meeting not found");
      }

      const data = await response.json();
      setMeetingData(data);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to load meeting data"
      );
    } finally {
      setLoading(false);
    }
  };

  const formatDateTime = (dateStr: string) => {
    const date = new Date(dateStr);
    return {
      date: date.toLocaleDateString("en-US", {
        weekday: "long",
        year: "numeric",
        month: "long",
        day: "numeric",
      }),
      time: date.toLocaleTimeString("en-US", {
        hour: "2-digit",
        minute: "2-digit",
        timeZoneName: "short",
      }),
    };
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.9)
      return "bg-green-100 text-green-800 border-green-200";
    if (confidence >= 0.7)
      return "bg-yellow-100 text-yellow-800 border-yellow-200";
    return "bg-red-100 text-red-800 border-red-200";
  };

  const getConfidenceLabel = (confidence: number) => {
    if (confidence >= 0.9) return "High Confidence";
    if (confidence >= 0.7) return "Medium Confidence";
    return "Low Confidence";
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading meeting availability...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
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
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.5 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"
              />
            </svg>
          </div>
          <h1 className="text-xl font-bold text-gray-900 mb-2">
            Meeting Not Found
          </h1>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={() => (window.location.href = "/connect")}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            Start New Meeting
          </button>
        </div>
      </div>
    );
  }

  if (!meetingData) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4">
        <div className="bg-white rounded-lg shadow-lg overflow-hidden">
          <div className="bg-blue-600 px-6 py-4">
            <h1 className="text-2xl font-bold text-white">
              Meeting Availability
            </h1>
            <p className="text-blue-100">Select your preferred meeting time</p>
          </div>

          <div className="p-6">
            <div className="mb-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-2">
                Participants
              </h2>
              <div className="flex flex-wrap gap-2">
                {meetingData.emails.map((email, index) => (
                  <span
                    key={index}
                    className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm"
                  >
                    {email}
                  </span>
                ))}
              </div>
            </div>

            <div className="mb-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                Proposed Times
              </h2>
              <div className="space-y-4">
                {meetingData.proposed_times.map((timeSlot, index) => {
                  const startTime = formatDateTime(timeSlot.start);
                  const endTime = formatDateTime(timeSlot.end);
                  const isSelected = selectedTime === index;

                  return (
                    <div
                      key={index}
                      onClick={() => setSelectedTime(index)}
                      className={`border-2 rounded-lg p-4 cursor-pointer transition-all ${
                        isSelected
                          ? "border-blue-500 bg-blue-50"
                          : "border-gray-200 hover:border-gray-300"
                      }`}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-4">
                            <div>
                              <h3 className="font-semibold text-gray-900">
                                {startTime.date}
                              </h3>
                              <p className="text-gray-600">
                                {startTime.time} - {endTime.time}
                              </p>
                            </div>
                            <span
                              className={`px-2 py-1 rounded-full text-xs font-medium border ${getConfidenceColor(
                                timeSlot.confidence
                              )}`}
                            >
                              {getConfidenceLabel(timeSlot.confidence)}
                            </span>
                          </div>
                        </div>
                        <div className="flex items-center">
                          {isSelected && (
                            <svg
                              className="w-6 h-6 text-blue-600"
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
                          )}
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {selectedTime !== null && (
              <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
                <h3 className="font-semibold text-green-900 mb-2">
                  Time Selected!
                </h3>
                <p className="text-green-800 text-sm">
                  You&apos;ve selected the meeting time. The organizer will be
                  notified and can send calendar invites.
                </p>
              </div>
            )}

            <div className="flex gap-4">
              <button
                disabled={selectedTime === null}
                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Confirm Selection
              </button>
              <button
                onClick={() => window.close()}
                className="px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-50"
              >
                Close
              </button>
            </div>
          </div>
        </div>

        <div className="mt-6 text-center">
          <p className="text-sm text-gray-500">
            Meeting ID: {meetingData.meeting_id}
          </p>
        </div>
      </div>
    </div>
  );
}
