'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { CheckCircle, ArrowRight, Sparkles } from 'lucide-react';
import Link from 'next/link';

export default function CheckoutSuccessPage() {
  const router = useRouter();
  const [countdown, setCountdown] = useState(5);

  useEffect(() => {
    const timer = setInterval(() => {
      setCountdown((prev) => {
        if (prev <= 1) {
          clearInterval(timer);
          router.push('/dashboard');
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [router]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-white to-blue-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 flex items-center justify-center px-4">
      <div className="max-w-2xl w-full">
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl p-8 md:p-12 text-center">
          {/* Success Icon */}
          <div className="flex justify-center mb-6">
            <div className="relative">
              <div className="absolute inset-0 bg-green-500 rounded-full animate-ping opacity-20"></div>
              <div className="relative bg-green-500 rounded-full p-4">
                <CheckCircle className="w-16 h-16 text-white" />
              </div>
            </div>
          </div>

          {/* Title */}
          <h1 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-4">
            Welcome to Premium! 🎉
          </h1>

          {/* Description */}
          <p className="text-lg text-gray-600 dark:text-gray-300 mb-8">
            Your subscription has been activated successfully. You now have unlimited access to all premium features!
          </p>

          {/* Features Unlocked */}
          <div className="bg-gradient-to-r from-blue-50 to-purple-50 dark:from-gray-700 dark:to-gray-600 rounded-xl p-6 mb-8">
            <div className="flex items-center justify-center gap-2 mb-4">
              <Sparkles className="w-5 h-5 text-blue-600 dark:text-blue-400" />
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                Features Unlocked
              </h2>
            </div>
            <ul className="space-y-2 text-left max-w-md mx-auto">
              <li className="flex items-center gap-3 text-gray-700 dark:text-gray-300">
                <CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0" />
                <span>Unlimited AI conversations</span>
              </li>
              <li className="flex items-center gap-3 text-gray-700 dark:text-gray-300">
                <CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0" />
                <span>All scenarios unlocked</span>
              </li>
              <li className="flex items-center gap-3 text-gray-700 dark:text-gray-300">
                <CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0" />
                <span>Offline mode enabled</span>
              </li>
              <li className="flex items-center gap-3 text-gray-700 dark:text-gray-300">
                <CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0" />
                <span>Advanced analytics</span>
              </li>
              <li className="flex items-center gap-3 text-gray-700 dark:text-gray-300">
                <CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0" />
                <span>Priority support</span>
              </li>
            </ul>
          </div>

          {/* Next Steps */}
          <div className="space-y-4">
            <Link
              href="/dashboard"
              className="inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-8 rounded-lg transition-all"
            >
              Go to Dashboard
              <ArrowRight className="w-5 h-5" />
            </Link>

            <p className="text-sm text-gray-500 dark:text-gray-400">
              Redirecting in {countdown} seconds...
            </p>
          </div>

          {/* Confirmation Email */}
          <div className="mt-8 pt-8 border-t border-gray-200 dark:border-gray-700">
            <p className="text-sm text-gray-600 dark:text-gray-400">
              📧 A confirmation email has been sent to your inbox with your receipt and subscription details.
            </p>
          </div>
        </div>

        {/* Support */}
        <div className="text-center mt-8">
          <p className="text-gray-600 dark:text-gray-400">
            Need help getting started?{' '}
            <a href="mailto:support@german-ai.com" className="text-blue-600 hover:text-blue-700 dark:text-blue-400">
              Contact Support
            </a>
          </p>
        </div>
      </div>
    </div>
  );
}
