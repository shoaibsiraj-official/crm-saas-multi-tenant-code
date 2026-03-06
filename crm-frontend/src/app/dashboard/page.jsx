import Link from "next/link";
import { ArrowRight, Users, Building2, FolderKanban, Receipt } from "lucide-react";

export default function DashboardHome() {
return ( <div className="space-y-8">
  {/* Page Heading */}
  <div>
    <h1 className="text-2xl font-bold text-slate-900">
      Dashboard
    </h1>
    <p className="text-slate-500 mt-1">
      Welcome back to your workspace.
    </p>
  </div>

  {/* Stats */}
  <div className="grid grid-cols-1 md:grid-cols-4 gap-6">

    <div className="p-6 bg-white rounded-xl border border-slate-200 shadow-sm">
      <Users className="w-6 h-6 text-blue-600 mb-3"/>
      <p className="text-sm text-slate-500">Members</p>
      <h3 className="text-xl font-semibold text-slate-900">124</h3>
    </div>

    <div className="p-6 bg-white rounded-xl border border-slate-200 shadow-sm">
      <Building2 className="w-6 h-6 text-green-600 mb-3"/>
      <p className="text-sm text-slate-500">Organizations</p>
      <h3 className="text-xl font-semibold text-slate-900">8</h3>
    </div>

    <div className="p-6 bg-white rounded-xl border border-slate-200 shadow-sm">
      <FolderKanban className="w-6 h-6 text-purple-600 mb-3"/>
      <p className="text-sm text-slate-500">Projects</p>
      <h3 className="text-xl font-semibold text-slate-900">26</h3>
    </div>

    <div className="p-6 bg-white rounded-xl border border-slate-200 shadow-sm">
      <Receipt className="w-6 h-6 text-orange-600 mb-3"/>
      <p className="text-sm text-slate-500">Invoices</p>
      <h3 className="text-xl font-semibold text-slate-900">14</h3>
    </div>

  </div>

  {/* Action Cards */}
  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">

    <div className="p-6 bg-white rounded-xl border border-slate-200 shadow-sm hover:shadow-md transition">
      <h3 className="font-semibold text-slate-900">
        Organization
      </h3>
      <p className="text-sm text-slate-500 mt-1 mb-4">
        Manage your organization details and branding.
      </p>

      <Link
        href="/organization"
        className="text-sm font-medium text-blue-600 hover:text-blue-700 flex items-center gap-1"
      >
        View Settings
        <ArrowRight className="w-4 h-4"/>
      </Link>
    </div>

    <div className="p-6 bg-white rounded-xl border border-slate-200 shadow-sm hover:shadow-md transition">
      <h3 className="font-semibold text-slate-900">
        Projects
      </h3>
      <p className="text-sm text-slate-500 mt-1 mb-4">
        Manage all your active projects.
      </p>

      <Link
        href="/projects"
        className="text-sm font-medium text-blue-600 hover:text-blue-700 flex items-center gap-1"
      >
        View Projects
        <ArrowRight className="w-4 h-4"/>
      </Link>
    </div>

    <div className="p-6 bg-white rounded-xl border border-slate-200 shadow-sm hover:shadow-md transition">
      <h3 className="font-semibold text-slate-900">
        Clients
      </h3>
      <p className="text-sm text-slate-500 mt-1 mb-4">
        Manage your clients and contacts.
      </p>

      <Link
        href="/clients"
        className="text-sm font-medium text-blue-600 hover:text-blue-700 flex items-center gap-1"
      >
        View Clients
        <ArrowRight className="w-4 h-4"/>
      </Link>
    </div>

  </div>

</div>


);
}
