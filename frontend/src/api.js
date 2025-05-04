// frontend/src/api.js
export async function pingBackend() {
    const res = await fetch(`${import.meta.env.VITE_API_URL}/ping`);
    const data = await res.json();
    return data;
  }
  