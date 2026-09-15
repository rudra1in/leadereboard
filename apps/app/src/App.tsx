import { Button } from "@repo/ui";
import type { User } from "@repo/shared-types";

export default function App() {
  const user: User = { id: 1, email: "demo@example.com", full_name: "Demo User" };
  return (
    <div style={{ padding: "2rem" }}>
      <h1>React SPA</h1>
      <p>Hello {user.full_name}</p>
      <Button>Click me</Button>
    </div>
  );
}
