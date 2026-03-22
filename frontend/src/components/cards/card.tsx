// This component accepts 'children' as a parameter
export default function Card({ children }: { children: React.ReactNode }) {
  return (
    <div style={{ border: '1px solid #ccc', padding: '20px', borderRadius: '8px' }}>
      {/* Whatever is passed inside the <Card> tags gets injected here */}
      {children}
    </div>
  );
}