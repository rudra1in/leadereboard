import { useState, useEffect } from "react";

interface Props {
  eventId: number;
}

export default function RegistrationForm({ eventId }: Props) {
  const [form, setForm] = useState({
    full_name: "",
    email: "",
    phone: "",
  });
  const [status, setStatus] = useState<"idle" | "submitting" | "processing" | "success" | "error">("idle");
  const [message, setMessage] = useState("");
  const [registrationId, setRegistrationId] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setStatus("submitting");

    try {
      const res = await fetch("http://localhost:8001/api/v1/registrations/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ event_id: eventId, ...form }),
      });

      const data = await res.json();
      setRegistrationId(data.registration_id);
      setStatus("processing");
      setMessage("Registration submitted. Waiting for confirmation...");
    } catch (err) {
      setStatus("error");
      setMessage("Failed to submit registration");
    }
  };

  // Listen to SSE
  useEffect(() => {
    if (!registrationId) return;

    const es = new EventSource(
      `http://localhost:8001/api/v1/sse/registrations/${registrationId}`
    );

    es.addEventListener("registration_update", (event) => {
      const data = JSON.parse(event.data);
      setStatus("success");
      setMessage(data.message || "Registration confirmed!");
      es.close();
    });

    es.onerror = () => {
      setStatus("error");
      setMessage("Connection lost");
      es.close();
    };

    return () => es.close();
  }, [registrationId]);

  return (
    <div className="border p-6 rounded-lg shadow">
      {status === "success" ? (
        <div className="text-green-600 font-medium">{message}</div>
      ) : (
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block mb-1">Full Name</label>
            <input
              required
              className="w-full border px-3 py-2 rounded"
              value={form.full_name}
              onChange={(e) => setForm({ ...form, full_name: e.target.value })}
            />
          </div>
          <div>
            <label className="block mb-1">Email</label>
            <input
              type="email"
              required
              className="w-full border px-3 py-2 rounded"
              value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })}
            />
          </div>
          <div>
            <label className="block mb-1">Phone</label>
            <input
              className="w-full border px-3 py-2 rounded"
              value={form.phone}
              onChange={(e) => setForm({ ...form, phone: e.target.value })}
            />
          </div>

          <button
            type="submit"
            disabled={status === "submitting" || status === "processing"}
            className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700 disabled:opacity-50"
          >
            {status === "submitting" && "Submitting..."}
            {status === "processing" && "Processing..."}
            {status === "idle" && "Register Now"}
          </button>

          {message && status !== "success" && (
            <p className="text-sm text-gray-600 mt-2">{message}</p>
          )}
        </form>
      )}
    </div>
  );
}