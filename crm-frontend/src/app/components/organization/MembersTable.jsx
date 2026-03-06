'use client';
import { MoreHorizontal } from 'lucide-react';
import Skeleton from '../ui/Skeleton';

export default function MembersTable({
  data = [],
  loading,
  onRoleChange,
  onRemove,
  currentUserId
}) {
  if (loading) {
    return (
      <div className="space-y-3">
        {[1, 2, 3].map((i) => (
          <Skeleton key={i} className="h-12 w-full" />
        ))}
      </div>
    );
  }

  const statusColors = {
    active: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400',
    pending: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400',
    inactive: 'bg-slate-100 text-slate-700 dark:bg-slate-700 dark:text-slate-300',
  };

  return (
    <div className="overflow-x-auto rounded-xl border border-slate-200 dark:border-slate-700">
      <table className="w-full text-sm">
        <thead className="bg-slate-50 dark:bg-slate-800/50 border-b border-slate-200 dark:border-slate-700">
          <tr>
            <th className="text-left py-3 px-4 font-medium">Member</th>
            <th className="text-left py-3 px-4 font-medium">Role</th>
            <th className="text-left py-3 px-4 font-medium">Status</th>
            <th className="text-right py-3 px-4 font-medium">Action</th>
          </tr>
        </thead>

        <tbody className="divide-y divide-slate-100 dark:divide-slate-700">
          {Array.isArray(data) &&
            data.map((member) => {

              // ✅ Safe ID handling
              const userId = member?.id;   // 🔥 ONLY THIS
              const isSelf = String(userId) === String(currentUserId);
              String(userId) === String(currentUserId);

              const name =
                member?.user?.name ||
                member?.name ||
                'Unknown';

              const email =
                member?.user?.email ||
                member?.email ||
                '';

              const role = member?.role || '';
              const status = member?.status || 'active';

              const initials = name
                ? name.split(' ').map(n => n[0]).join('')
                : '?';

              return (
                <tr
                  key={member.id}
                  className="hover:bg-slate-50 dark:hover:bg-slate-800/30 transition-colors"
                >
                  {/* MEMBER */}
                  <td className="py-3 px-4">
                    <div className="flex items-center gap-3">
                      <div className="w-9 h-9 rounded-full bg-slate-200 dark:bg-slate-700 flex items-center justify-center text-xs font-medium text-slate-600 dark:text-slate-300">
                        {initials}
                      </div>

                      <div>
                        <p className="font-medium text-slate-900 dark:text-white">
                          {name}
                        </p>
                        <p className="text-xs text-slate-500 dark:text-slate-400">
                          {email}
                        </p>
                      </div>
                    </div>
                  </td>

                  {/* ROLE */}
                  <td className="py-3 px-4">
                    {isSelf ? (
                      <span className="text-slate-400 text-sm">
                        {role} (You)
                      </span>
                    ) : (
                      <select
                        value={role}
                        onChange={(e) =>
                          onRoleChange(userId, e.target.value)
                        }
                        className="px-2 py-1 rounded border bg-white dark:bg-slate-800 text-sm"
                      >
                        <option value="MEMBER">Member</option>
                        <option value="ORG_ADMIN">Admin</option>
                      </select>
                    )}
                  </td>
                  {/* {Remove} */}
                  <td className="py-3 px-4 text-right">
                    {!isSelf && (
                      <button
                        onClick={() => onRemove(userId)}
                        className="text-red-600 hover:text-red-700 text-sm font-medium"
                      >
                        Remove
                      </button>
                    )}
                  </td>

                  {/* STATUS */}
                  <td className="py-3 px-4">
                    <span
                      className={`px-2.5 py-1 rounded-full text-xs font-medium capitalize ${statusColors[status] || statusColors.active
                        }`}
                    >
                      {status}
                    </span>
                  </td>

                  {/* ACTION */}
                  <td className="py-3 px-4 text-right">
                    <button className="p-1.5 hover:bg-slate-100 dark:hover:bg-slate-700 rounded-md text-slate-500">
                      <MoreHorizontal className="w-4 h-4" />
                    </button>
                  </td>
                </tr>
              );
            })}
        </tbody>
      </table>
    </div>
  );
}