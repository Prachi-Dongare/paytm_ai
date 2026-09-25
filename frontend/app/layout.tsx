import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "ReconcileAI | Merchant Operations",
  description:
    "Autonomous merchant payment reconciliation and exception management.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}