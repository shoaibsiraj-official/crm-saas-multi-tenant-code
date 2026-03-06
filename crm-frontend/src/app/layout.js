import './globals.css';
import Navbar from './components/layout/Navbar';
import AuthProvider from './components/providers/AuthProvider';
import { Toaster } from 'react-hot-toast';

export const metadata = {
title: 'SaaSKit - Authentication',
description: 'Production Ready Next.js Authentication',
};

export default function RootLayout({ children }) {
return ( <html lang="en"> <body className="w-full min-h-screen bg-white">
    <AuthProvider>

      <Navbar />

      <main className="w-full min-h-screen">
        {children}
      </main>

      <Toaster position="top-right" />

    </AuthProvider>

  </body>
</html>

);
}
