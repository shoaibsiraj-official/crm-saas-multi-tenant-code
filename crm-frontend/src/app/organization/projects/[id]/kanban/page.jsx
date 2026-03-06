'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';

import {
  DndContext,
  closestCenter,
  KeyboardSensor,
  PointerSensor,
  useSensor,
  useSensors,
  useDroppable
} from '@dnd-kit/core';

import {
  sortableKeyboardCoordinates,
  useSortable,
  verticalListSortingStrategy,
  SortableContext
} from '@dnd-kit/sortable';

import { CSS } from '@dnd-kit/utilities';

import { getProjectTasks, updateTask } from '@/lib/project';
import Card from '@/app/components/ui/Card';
import Badge from '@/app/components/ui/Badge';
import Avatar from '@/app/components/ui/Avatar';
import toast from 'react-hot-toast';


/* ✅ Backend Status Match */
const columns = [
  { id: 'TODO', title: 'Todo' },
  { id: 'IN_PROGRESS', title: 'In Progress' },
  { id: 'REVIEW', title: 'Review' },
  { id: 'DONE', title: 'Done' },
];


/* ---------------- DROPPABLE COLUMN ---------------- */

function KanbanColumn({ column, tasks }) {
  const { setNodeRef } = useDroppable({
    id: column.id
  });

  return (
    <div
      ref={setNodeRef}
      className="bg-slate-100 dark:bg-slate-800/50 rounded-xl p-4 flex flex-col min-h-[500px]"
    >
      <div className="flex justify-between items-center mb-4">
        <h3 className="font-semibold text-sm">{column.title}</h3>
        <span className="text-xs bg-slate-200 px-2 py-0.5 rounded-full">
          {tasks.length}
        </span>
      </div>

      <SortableContext
        items={tasks.map(t => t.id)}
        strategy={verticalListSortingStrategy}
      >
        <div className="flex-1">
          {tasks.map(task => (
            <KanbanCard key={task.id} task={task} />
          ))}
        </div>
      </SortableContext>
    </div>
  );
}


/* ---------------- CARD ---------------- */

function KanbanCard({ task }) {
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition
  } = useSortable({ id: task.id });

  const style = {
    transition,
    transform: CSS.Transform.toString(transform),
  };

  return (
    <div ref={setNodeRef} style={style} {...attributes} {...listeners}>
      <Card className="p-3 mb-3 cursor-grab active:cursor-grabbing hover:border-indigo-400">
        <p className="font-medium text-sm mb-2">{task.title}</p>

        <div className="flex items-center justify-between">
          <Avatar name={task.assigned_to?.full_name || 'U'} className="w-6 h-6 text-[10px]" />

          <Badge
            variant={
              task.priority === 'HIGH'
                ? 'danger'
                : task.priority === 'MEDIUM'
                ? 'warning'
                : 'default'
            }
          >
            {task.priority}
          </Badge>
        </div>
      </Card>
    </div>
  );
}


/* ---------------- MAIN PAGE ---------------- */

export default function KanbanPage() {

  const params = useParams();
  const id = params?.id;
  console.log("Params:", params);
  console.log("Project ID:", id);

  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);

  const sensors = useSensors(
    useSensor(PointerSensor),
    useSensor(KeyboardSensor, {
      coordinateGetter: sortableKeyboardCoordinates
    })
  );


  /* ---------- FETCH ---------- */

  useEffect(() => {
    if (!id) return;

    const fetchTasks = async () => {
      try {
        const data = await getProjectTasks(id);
        setTasks(Array.isArray(data) ? data : []);
      } catch {
        toast.error("Failed to load tasks");
      } finally {
        setLoading(false);
      }
    };

    fetchTasks();
  }, [id]);


  /* ---------- DRAG ---------- */

  const handleDragEnd = async (event) => {
    const { active, over } = event;
    if (!over) return;

    const taskId = active.id;

    // 🔥 Find destination column
    const overColumn = columns.find(col => col.id === over.id);

    let newStatus;

    if (overColumn) {
      newStatus = overColumn.id;
    } else {
      // Dropped over another task
      const overTask = tasks.find(t => t.id === over.id);
      if (!overTask) return;
      newStatus = overTask.status;
    }

    const task = tasks.find(t => t.id === taskId);
    if (!task || task.status === newStatus) return;

    // Optimistic update
    const updated = tasks.map(t =>
      t.id === taskId ? { ...t, status: newStatus } : t
    );

    setTasks(updated);

    try {
      await updateTask(taskId, { status: newStatus });
      toast.success("Task moved");
    } catch {
      toast.error("Move failed");
      const fresh = await getProjectTasks(id);
      setTasks(fresh);
    }
  };


  if (loading) {
    return <div className="p-6 text-center">Loading...</div>;
  }


  return (
    <DndContext
      sensors={sensors}
      collisionDetection={closestCenter}
      onDragEnd={handleDragEnd}
    >
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        {columns.map(col => (
          <KanbanColumn
            key={col.id}
            column={col}
            tasks={tasks.filter(t => t.status === col.id)}
          />
        ))}
      </div>
    </DndContext>
  );
}