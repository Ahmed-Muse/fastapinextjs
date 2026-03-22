
import "./globals.css";

export default function RootLayout({children,}: {children: React.ReactNode;}) 

{
  return (
    <html lang="en">
      <body className="bg-slate-100 text-slate-800">
        <main>
        {children}
        </main>
        <footer className="py-6 px-4 text-center text-slate-500 text-sm text-color-slate-blue-500 border-t border-slate-300 mt-10 bg-slate-50 shadow-inner">
          My Footer
        </footer>
      </body>
    </html>
  );
}
