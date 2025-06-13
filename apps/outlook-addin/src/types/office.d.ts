// Type definitions for Office.js specific to our SmartMeet add-in

declare global {
  namespace Office {
    interface EmailAddressDetails {
      emailAddress: string;
      displayName?: string;
    }

    interface Context {
      mailbox: {
        item: {
          to?: EmailAddressDetails[];
          cc?: EmailAddressDetails[];
          body?: {
            setSelectedDataAsync: (
              data: string,
              options: { coercionType: any },
              callback: (result: { status: any; error?: any }) => void
            ) => void;
          };
        };
      };
    }

    const context: Context;

    enum HostType {
      Outlook = "Outlook",
    }

    enum CoercionType {
      Text = "text",
    }

    enum AsyncResultStatus {
      Succeeded = "succeeded",
    }

    function onReady(callback: (info: { host: HostType }) => void): void;
  }
}

export {};
