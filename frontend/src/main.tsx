import React from "react";
import ReactDOM from "react-dom/client";
import { Toaster } from "sonner";
import { ThemeProvider } from "@providers/ThemeProvider";
import { QueryProvider } from "@providers/QueryProvider";
import { AppRouter } from "@routes/index";
import "@styles/globals.css";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <ThemeProvider>
      <QueryProvider>
        <AppRouter />
        <Toaster position="top-right" richColors />
      </QueryProvider>
    </ThemeProvider>
  </React.StrictMode>,
);
