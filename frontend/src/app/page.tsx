import AppLayout from "../components/AppLayout"; 

export default function HomePage() {
  return (
    <AppLayout>
      {/* EVERYTHING HERE gets injected where {children} is in AppLayout */}
      <div>
        <h1 className="text-2xl font-bold mb-4">Dashboard Overview</h1>
        <p>Welcome to the AI Product Sizing Engine. This content is seamlessly injected into the layout.</p>
      </div>
    </AppLayout>
  );
}