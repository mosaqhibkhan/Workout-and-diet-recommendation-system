const API_BASE_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:3000";

export async function getWorkoutPlan(formData) {
  let response;

  try {
    response = await fetch(`${API_BASE_URL}/predict`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(formData),
    });
  } catch {
    throw new Error("Could not reach the server. Make sure the backend is running.");
  }

  const data = await response.json().catch(() => null);

  if (!response.ok || !data) {
    throw new Error(data?.error || "Something went wrong.");
  }

  return data;
}
