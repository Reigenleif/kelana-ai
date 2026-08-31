import Navbar from '@/components/Navbar';
import './globals.css';

export const metadata = {
  title: 'Kelana AI - Smart Travel Planner & AI Itineraries',
  description: 'AI-powered travel recommendations and daily itineraries powered by AWS Bedrock and vibrant community chat.',
};

export default function RootLayout({ children }) {
  return (
    <html lang="en" className="dark">
      <body className="bg-[#090d14] text-slate-100 min-h-screen flex flex-col antialiased selection:bg-rose-500 selection:text-white">
        <Navbar />
        <main className="flex-1 w-full">{children}</main>
      </body>
    </html>
  );
}
