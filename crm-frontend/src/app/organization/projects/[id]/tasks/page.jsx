"use client";

import { useState, useEffect } from "react";
import { useParams } from "next/navigation";

import {
  getProjectTasks,
  createTask,
  deleteTask
} from "@/lib/project";

import { getMembers } from "@/lib/organization";

import Card from "@/app/components/ui/Card";
import Button from "@/app/components/ui/Button";
import Badge from "@/app/components/ui/Badge";
import Avatar from "@/app/components/ui/Avatar";
import Modal from "@/app/components/ui/Modal";
import InputField from "@/app/components/ui/InputField";
import EmptyState from "@/app/components/ui/EmptyState";

import toast from "react-hot-toast";
import { Plus, Trash2, Search } from "lucide-react";

export default function TaskListPage() {

  /* ---------------- GET PROJECT ID ---------------- */

  const params = useParams();
  const projectId = Array.isArray(params?.id)
    ? params.id[0]
    : params?.id;

  /* ---------------- STATE ---------------- */

  const [tasks, setTasks] = useState([]);
  const [members, setMembers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setModalOpen] = useState(false);
  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState("");

  const [taskForm, setTaskForm] = useState({
    title: "",
    assigned_to: null,
    priority: "MEDIUM",
    due_date: null,
    status: "TODO",
  });

  /* ---------------- FETCH TASKS ---------------- */

  useEffect(() => {
    if (!projectId) return;

    fetchTasks();
    fetchMembers();
  }, [projectId]);

  const fetchTasks = async () => {
    try {
      const data = await getProjectTasks(projectId);
      console.log("FETCHED DATA:", data);
      setTasks(data);
    } catch (error) {
      toast.error("Could not load tasks");
    } finally {
      setLoading(false);
    }
  };

  const fetchMembers = async () => {
    try {
      const res = await getMembers();
      setMembers(Array.isArray(res) ? res : res?.data || []);
    } catch {
      setMembers([]);
    }
  };

  /* ---------------- CREATE TASK ---------------- */

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!projectId) {
      toast.error("Project ID missing");
      return;
    }

    try {
      const payload = {
        title: taskForm.title,
        assigned_to: taskForm.assigned_to || null,
        priority: taskForm.priority,
        status: taskForm.status,
        due_date: taskForm.due_date || null,
      };

      console.log("Sending payload:", payload);

      await createTask(projectId, payload);

      toast.success("Task created");
      setModalOpen(false);
      fetchTasks();
      resetForm();

    } catch (error) {
      console.log("TASK ERROR:", error?.response?.data);
      toast.error("Error saving task");
    }
  };

  /* ---------------- DELETE ---------------- */

  const handleDelete = async (taskId) => {
    if (!confirm("Are you sure?")) return;

    try {
      await deleteTask(taskId);
      toast.success("Task deleted");
      fetchTasks();
    } catch {
      toast.error("Delete failed");
    }
  };

  /* ---------------- RESET FORM ---------------- */

  const resetForm = () => {
    setTaskForm({
      title: "",
      assigned_to: null,
      priority: "MEDIUM",
      due_date: null,
      status: "TODO",
    });
  };

  /* ---------------- FILTER ---------------- */

  const filteredTasks = tasks.filter((t) =>
    t.title?.toLowerCase().includes(search.toLowerCase()) &&
    (filter ? t.status === filter : true)
  );

  const priorityColors = {
    LOW: "default",
    MEDIUM: "warning",
    HIGH: "danger",
  };

  const statusColors = {
    TODO: "default",
    IN_PROGRESS: "primary",
    REVIEW: "warning",
    DONE: "success",
  };

  /* ---------------- UI ---------------- */

  return (
    <div className="space-y-4">

      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between gap-4">

        <div className="flex gap-3 flex-1">

          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <input
              type="text"
              placeholder="Search tasks..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="pl-9 pr-4 py-2 rounded-lg border text-sm w-full"
            />
          </div>

          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="px-3 py-2 rounded-lg border text-sm"
          >
            <option value="">All</option>
            <option value="TODO">Todo</option>
            <option value="IN_PROGRESS">In Progress</option>
            <option value="REVIEW">Review</option>
            <option value="DONE">Done</option>
          </select>

        </div>

        <Button
          onClick={() => {
            resetForm();
            setModalOpen(true);
          }}
        >
          <Plus className="w-4 h-4 mr-2" />
          Add Task
        </Button>

      </div>

      {/* Table */}
      <Card className="overflow-hidden">

        {loading ? (
          <div className="p-8 text-center">Loading...</div>
        ) : filteredTasks.length === 0 ? (
          <EmptyState title="No tasks" description="Create your first task." />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">

              <thead className="bg-slate-50">
                <tr>
                  <th className="text-left px-4 py-3">Task</th>
                  <th className="text-left px-4 py-3">Assignee</th>
                  <th className="text-left px-4 py-3">Priority</th>
                  <th className="text-left px-4 py-3">Status</th>
                  <th className="text-right px-4 py-3">Actions</th>
                </tr>
              </thead>

              <tbody className="divide-y">
                {filteredTasks.map((task) => (
                  <tr key={task.id}>
                    <td className="px-4 py-3">{task.title}</td>

                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <Avatar name={task.assigned_to?.full_name || "U"} />
                        <span className="text-xs">
                          {task.assigned_to?.full_name || "Unassigned"}
                        </span>
                      </div>
                    </td>

                    <td className="px-4 py-3">
                      <Badge variant={priorityColors[task.priority]}>
                        {task.priority}
                      </Badge>
                    </td>

                    <td className="px-4 py-3">
                      <Badge variant={statusColors[task.status]}>
                        {task.status}
                      </Badge>
                    </td>

                    <td className="px-4 py-3 text-right">
                      <button
                        onClick={() => handleDelete(task.id)}
                        className="p-1.5 hover:bg-red-100 rounded-md"
                      >
                        <Trash2 className="w-4 h-4 text-red-500" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>

            </table>
          </div>
        )}

      </Card>

      {/* Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setModalOpen(false)}
        title="Create Task"
      >
        <form onSubmit={handleSubmit} className="space-y-4">

          {/* Title */}
          <InputField
            label="Title"
            value={taskForm.title}
            onChange={(e) =>
              setTaskForm({ ...taskForm, title: e.target.value })
            }
            required
          />

          {/* Assignee */}
          <div>
            <label className="block text-sm font-medium mb-1">
              Assignee
            </label>
            <select
              value={taskForm.assigned_to || ""}
              onChange={(e) =>
                setTaskForm({
                  ...taskForm,
                  assigned_to: e.target.value || null,
                })
              }
              className="w-full px-3 py-2 rounded-lg border text-sm"
            >
              <option value="">Unassigned</option>
              {members.map((m) => (
                <option key={m.id} value={m.id}>
                  {m.full_name}
                </option>
              ))}
            </select>
          </div>

          {/* Priority */}
          <div>
            <label className="block text-sm font-medium mb-1">
              Priority
            </label>
            <select
              value={taskForm.priority}
              onChange={(e) =>
                setTaskForm({
                  ...taskForm,
                  priority: e.target.value,
                })
              }
              className="w-full px-3 py-2 rounded-lg border text-sm"
            >
              <option value="LOW">Low</option>
              <option value="MEDIUM">Medium</option>
              <option value="HIGH">High</option>
            </select>
          </div>

          {/* Status */}
          <div>
            <label className="block text-sm font-medium mb-1">
              Status
            </label>
            <select
              value={taskForm.status}
              onChange={(e) =>
                setTaskForm({
                  ...taskForm,
                  status: e.target.value,
                })
              }
              className="w-full px-3 py-2 rounded-lg border text-sm"
            >
              <option value="TODO">Todo</option>
              <option value="IN_PROGRESS">In Progress</option>
              <option value="REVIEW">Review</option>
              <option value="DONE">Done</option>
            </select>
          </div>

          {/* Due Date */}
          <div>
            <label className="block text-sm font-medium mb-1">
              Due Date
            </label>
            <input
              type="date"
              value={taskForm.due_date || ""}
              onChange={(e) =>
                setTaskForm({
                  ...taskForm,
                  due_date: e.target.value || null,
                })
              }
              className="w-full px-3 py-2 rounded-lg border text-sm"
            />
          </div>

          {/* Buttons */}
          <div className="flex justify-end gap-3 pt-4">
            <Button
              variant="secondary"
              onClick={() => setModalOpen(false)}
            >
              Cancel
            </Button>
            <Button type="submit">Create</Button>
          </div>

        </form>
      </Modal>

    </div>
  );
}