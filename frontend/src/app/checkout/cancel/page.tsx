'use client';

import { XCircle, ArrowLeft, HelpCircle } from 'lucide-react';
import Link from 'next/link';

export default function CheckoutCancelPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-red-50 via-white to-orange-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 flex items-center justify-center px-4">
      <div className="max-w-2xl w-full">
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl p-8 md:p-12 text-center">
          {/* Cancel Icon */}
          <div className="flex justify-center mb-6">
            <div className="bg-red-100 dark:bg-red-900 rounded-full p-4">
              <XCircle className="w-16 h-16 text-red-600 dark:text-red-400" />
            </div>
          </div>

          {/* Title */}
          <h1 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-4">
            Checkout Cancelled
          </h1>

          {/* Description */}
          <p className="text-lg text-gray-600 dark:text-gray-300 mb-8">
            Your payment was cancelled. No charges were made to your account.
          </p>

          {/* Reasons */}
          <div className="bg-gray-50 dark:bg-gray-700 rounded-xl p-6 mb-8">
            <div className="flex items-center justify-center gap-2 mb-4">
              <HelpCircle className="w-5 h-5 text-gray-600 dark:text-gray-400" />
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                Common Reasons
              </h2>
            </div>
            <ul className="space-y-2 text-left max-w-md mx-auto text-gray-700 dark:text-gray-300">
              <li>• Changed your mind</li>
              <li>• Want to review features first</li>
              <li>• Payment method issue</li>
              <li>• Need to discuss with team</li>
            </ul>
          </div>

          {/* Actions */}
          <div className="space-y-4">
            <Link
              href="/pricing"
              className="inline-flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-8 rounded-lg transition-all"
            >
              <ArrowLeft className="w-5 h-5" />
              Back to Pricing
            </Link>

            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                href="/dashboard"
                className="text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white font-medium"
              >
                Continue with Free Plan
              </Link>
              <a
                href="mailto:support@german-ai.com"
                className="text-blue-600 hover:text-blue-700 dark:text-blue-400 font-medium"
              >
                Contact Support
              </a>
            </div>
          </div>

          {/* Reassurance */}
          <div className="mt-8 pt-8 border-t border-gray-200 dark:border-gray-700">
            <p className="text-sm text-gray-600 dark:text-gray-400">
              💡 You can still enjoy our free plan with 30 minutes of AI conversation per day.
              Upgrade anytime when you're ready!
            </p>
          </div>
        </div>

        {/* Help */}
        <div className="text-center mt-8">
          <p className="text-gray-600 dark:text-gray-400">
            Have questions?{' '}
            <a href="mailto:support@german-ai.com" className="text-blue-600 hover:text-blue-700 dark:text-blue-400">
              We're here to help
            </a>
          </p>
        </div>
      </div>
    </div>
  );
}
