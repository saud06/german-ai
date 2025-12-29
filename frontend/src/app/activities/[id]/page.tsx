'use client';

import { useParams, useSearchParams, useRouter } from 'next/navigation';
import { useEffect } from 'react';

export default function UnifiedActivityPage() {
  const params = useParams();
  const searchParams = useSearchParams();
  const router = useRouter();
  const activityId = params.id as string;
  const activityType = searchParams.get('type');

  useEffect(() => {
    // Redirect to appropriate page based on activity type
    if (activityType === 'scenario') {
      router.replace(`/scenarios/${activityId}`);
    } else if (activityType === 'vocabulary') {
      router.replace(`/vocab?activity_id=${activityId}`);
    } else if (activityType === 'quiz') {
      router.replace(`/quiz?activity_id=${activityId}`);
    } else if (activityType === 'grammar') {
      router.replace(`/grammar?activity_id=${activityId}`);
    } else {
      // Unknown activity type, go back to learning path
      router.replace('/learning-path');
    }
  }, [activityType, activityId, router]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-50 flex items-center justify-center">
      <div className="text-center">
        <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-indigo-600 mx-auto"></div>
        <p className="mt-4 text-gray-600">Loading activity...</p>
      </div>
    </div>
  );
}
