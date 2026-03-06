import Sidebar from "../components/layout/Sidebar";
import { Toaster } from "react-hot-toast";

export default function DashboardLayout({ children }) {
return ( <div className="flex w-full h-screen overflow-hidden bg-white">
  {/* Sidebar */}
  <Sidebar />

  {/* Main Content */}
  <div className="flex flex-col flex-1 w-full h-full">

    {/* Header */}
    <header className="h-16 w-full border-b border-slate-200 flex items-center px-8 bg-white">
      <h1 className="text-lg font-semibold text-slate-800">
        CRM Dashboard
      </h1>
    </header>

    {/* Content */}
    <main className="flex-1 w-full overflow-y-auto p-8">
      {children}
    </main>

  </div>

  <Toaster position="top-right" />
</div>
);
}
