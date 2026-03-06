import api from './axios';

/* =========================
   Organization Detail
========================= */
export const getOrganization = async () => {
  const res = await api.get('/organizations/me/');
  return res.data.data;   // unwrap backend response
};
export const getOrganizationDetail = async () => {
  const res = await api.get('/organizations/me/');
  return res.data.data;
};
/* =========================
   Update Organization
========================= */
export const updateOrganization = async (data) => {
  const res = await api.patch('/organizations/update/', data);
  return res.data.data;
};

/* =========================
   Members List
========================= */
export const getMembers = async () => {
  const res = await api.get('/organizations/members/');
  return res.data.data.members;   // ✅ FIXED
};

/* =========================
   Invite Member
========================= */
export const inviteMember = async (email, role) => {
  const res = await api.post('/organizations/invite/', {
    email,
    role,
  });

  return res.data.data;   // ✅ FIXED 
};

export const updateMemberRole = async (userId, role) => {
  const res = await api.patch(
    `/organizations/members/${userId}/role/`,
    { role }
  );

  return res.data.data;
};

export const removeMember = async (userId) => {
  const res = await api.delete(
    `/organizations/members/${userId}/`
  );
  return res.data.data;
};


export const acceptInvite = async (token) => {
  const res = await api.post('/organizations/invite/accept/', {
    token,
  });

  return res.data.data;
};

export const getInvites = async () => {
  const res = await api.get('/organizations/invites/');
  return res.data.data.invites;
};

export const revokeInvite = async (inviteId) => {
  const res = await api.delete(`/organizations/invites/${inviteId}/`);
  return res.data.data;
};