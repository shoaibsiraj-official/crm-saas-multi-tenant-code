"use client";

import { useState, useEffect } from "react";
import { useRouter, useParams } from "next/navigation";
import { updateProject, deleteProject, getProject } from "@/lib/project";

import Card from "@/app/components/ui/Card";
import Button from "@/app/components/ui/Button";
import InputField from "@/app/components/ui/InputField";
import Modal from "@/app/components/ui/Modal";

import toast from "react-hot-toast";
import { Trash2, Archive } from "lucide-react";

export default function ProjectSettingsPage() {

  const router = useRouter();
  const params = useParams();
  const projectId = params?.id;

  const [project, setProject] = useState(null);
  const [name, setName] = useState("");
  const [status, setStatus] = useState("ACTIVE");
  const [deleteModal, setDeleteModal] = useState(false);
  const [loading, setLoading] = useState(false);

  /* ---------------- FETCH PROJECT ---------------- */

  useEffect(() => {
    if (!projectId) return;

    const fetchProject = async () => {
      try {
        const res = await getProject(projectId);
        setProject(res);
        setName(res.name);
        setStatus(res.status);
      } catch {
        toast.error("Failed to load project");
      }
    };

    fetchProject();
  }, [projectId]);

  /* ---------------- SAVE CHANGES ---------------- */

  const handleSave = async () => {
    console.log("Saving:", name, status);

    try {
      const res = await updateProject(projectId, {
        name,
        status,
      });

      console.log("API RESPONSE:", res);

      toast.success("Project updated");
      router.push(`/organization/projects/`);
    } catch (error) {
      console.log("UPDATE ERROR:", error.response?.data);
      toast.error("Update failed");
    }
  };

  /* ---------------- ARCHIVE ---------------- */

  const handleArchive = async () => {
    try {
      await updateProject(projectId, { status: "ARCHIVED" });
      setStatus("ARCHIVED");
      toast.success("Project archived");
    } catch {
      toast.error("Error archiving");
    }
  };

  /* ---------------- DELETE ---------------- */

  const handleDelete = async () => {
    setLoading(true);

    try {
      await deleteProject(projectId);
      toast.success("Project deleted");
      router.push("/organization/projects");
    } catch {
      toast.error("Error deleting");
      setLoading(false);
    }
  };

  if (!project) {
    return <div className="p-8 text-center">Loading...</div>;
  }

  return (
    <div className="max-w-3xl mx-auto space-y-8">

      {/* ---------------- GENERAL SETTINGS ---------------- */}

      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-6">
          General Settings
        </h3>

        <div className="space-y-4">

          <InputField
            label="Project Name"
            value={name}
            onChange={(e) => setName(e.target.value)}
          />

          <div>
            <label className="block text-sm font-medium mb-1">
              Status
            </label>

            <select
              value={status}
              onChange={(e) => setStatus(e.target.value)}
              className="w-full px-3 py-2 rounded-lg border"
            >
              <option value="ACTIVE">Active</option>
              <option value="COMPLETED">Completed</option>
              <option value="ARCHIVED">Archived</option>
            </select>
          </div>

          <Button onClick={handleSave}>
            Save Changes
          </Button>

        </div>
      </Card>

      {/* ---------------- DANGER ZONE ---------------- */}

      <Card className="p-6 border-red-200">
        <h3 className="text-lg font-semibold text-red-600 mb-2">
          Danger Zone
        </h3>

        <p className="text-sm mb-6">
          Irreversible and destructive actions.
        </p>

        <div className="flex gap-4">

          <Button variant="secondary" onClick={handleArchive}>
            <Archive className="w-4 h-4 mr-2" />
            Archive Project
          </Button>

          <Button
            className="bg-red-600 hover:bg-red-700"
            onClick={() => setDeleteModal(true)}
          >
            <Trash2 className="w-4 h-4 mr-2" />
            Delete Project
          </Button>

        </div>
      </Card>

      {/* ---------------- DELETE MODAL ---------------- */}

      <Modal
        isOpen={deleteModal}
        onClose={() => setDeleteModal(false)}
        title="Delete Project"
      >
        <p className="mb-6">
          Are you sure you want to delete this project?
          This action cannot be undone.
        </p>

        <div className="flex justify-end gap-3">
          <Button variant="secondary" onClick={() => setDeleteModal(false)}>
            Cancel
          </Button>

          <Button
            onClick={handleDelete}
            isLoading={loading}
            className="bg-red-600 hover:bg-red-700"
          >
            Delete Project
          </Button>
        </div>
      </Modal>

    </div>
  );
}