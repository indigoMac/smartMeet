Office.onReady(() => {
  // Register command functions
});

// Function to handle the taskpane command
function showTaskpane(event: any) {
  // This is handled by the manifest, no action needed
  event.completed();
}

// Make functions available globally
(global as any).showTaskpane = showTaskpane;
