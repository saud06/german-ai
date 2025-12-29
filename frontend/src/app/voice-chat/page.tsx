import dynamic from 'next/dynamic';
import RequireAuth from '@/components/RequireAuth';

const VoiceChatClient = dynamic(() => import('./VoiceChatClient'), {
  ssr: false,
  loading: () => (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-4 flex items-center justify-center">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
        <p className="text-gray-600">Loading Voice Chat...</p>
      </div>
    </div>
  ),
});

export default function Page() {
  return (
    <>
      <RequireAuth />
      <VoiceChatClient />
    </>
  );
}
