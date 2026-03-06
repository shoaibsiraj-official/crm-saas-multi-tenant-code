"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Cookies from "js-cookie";
import api from "@/lib/axios";
import toast from "react-hot-toast";

export default function AcceptInvitePage() {
  const { token } = useParams();
  const router = useRouter();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const processInvite = async () => {
      try {
        // If not logged in → redirect to login first
        const access = Cookies.get("access_token");

        if (!access) {
          router.push(`/login?invite=${token}`);
          return;
        }
        if (!user) {
          router.push(`/login?invite=${token}`);
          return;
        }

        await api.post("/organizations/invite/accept/", {
          token,
        });

        toast.success("Invitation accepted successfully!");
        router.push("/dashboard");

      } catch (err) {
        toast.error("Invite invalid or expired.");
        router.push("/dashboard");
      } finally {
        setLoading(false);
      }
    };

    if (token) processInvite();
  }, [token]);

  return (
    <div className="flex items-center justify-center h-screen">
      {loading && <p>Processing invitation...</p>}
    </div>
  );
}