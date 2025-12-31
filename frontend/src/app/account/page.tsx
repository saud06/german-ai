'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import RequireAuth from '@/components/RequireAuth';

interface PricingTier {
  id: string;
  name: string;
  price: number | null;
  interval: string;
  features: string[];
  popular?: boolean;
}

interface Subscription {
  tier: string;
  status: string;
  current_period_end: string | null;
  cancel_at_period_end: boolean;
}

interface ReferralStats {
  code: string;
  total_referrals: number;
  successful_referrals: number;
  pending_referrals: number;
  total_rewards: number;
}

export default function AccountPage() {
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<'subscription' | 'referrals'>('subscription');
  const [subscription, setSubscription] = useState<Subscription | null>(null);
  const [referralStats, setReferralStats] = useState<ReferralStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);

  const pricingTiers: PricingTier[] = [
    {
      id: 'free',
      name: 'Free',
      price: 0,
      interval: 'forever',
      features: [
        '5 AI conversations per day',
        'Basic vocabulary (500 words)',
        'Grammar lessons',
        'Public quizzes',
        'Community support'
      ]
    },
    {
      id: 'premium',
      name: 'Premium',
      price: 999,
      interval: 'month',
      popular: true,
      features: [
        'Unlimited AI conversations',
        'Full vocabulary (5000+ words)',
        'Advanced grammar',
        'Unlimited quizzes',
        'Voice chat',
        'Spaced repetition',
        'Priority support'
      ]
    },
    {
      id: 'plus',
      name: 'Plus',
      price: 1999,
      interval: 'month',
      features: [
        'Everything in Premium',
        'Business German',
        'Certification prep',
        'Custom learning paths',
        'Advanced analytics',
        'API access',
        '1-on-1 tutoring (2h/month)'
      ]
    }
  ];

  useEffect(() => {
    fetchAccountData();
  }, []);

  const fetchAccountData = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        router.push('/login');
        return;
      }

      // Fetch subscription
      const subResponse = await fetch('http://localhost:8000/api/v1/payments/subscription', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (subResponse.ok) {
        const subData = await subResponse.json();
        setSubscription(subData);
      }

      // Fetch referral stats
      const refResponse = await fetch('http://localhost:8000/api/v1/referrals/stats', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (refResponse.ok) {
        const refData = await refResponse.json();
        setReferralStats(refData);
      }
    } catch (error) {
    } finally {
      setLoading(false);
    }
  };

  const handleUpgrade = async (tierId: string) => {
    if (tierId === 'free') return;

    setActionLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8000/api/v1/payments/create-checkout-session', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          tier: tierId,
          success_url: `${window.location.origin}/account?success=true`,
          cancel_url: `${window.location.origin}/account`,
          trial_days: subscription?.tier === 'free' ? 14 : undefined
        })
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Failed to create checkout session');
      }

      const data = await response.json();
      if (data.checkout_url) {
        window.location.href = data.checkout_url;
      }
    } catch (error: any) {
      const message = error.message || 'Failed to start checkout';
      if (message.includes('Stripe')) {
        alert('Payment system is not fully configured. Please contact support.');
      } else {
        alert(message);
      }
    } finally {
      setActionLoading(false);
    }
  };

  const generateReferralCode = async () => {
    setActionLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8000/api/v1/referrals/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        await fetchAccountData();
      }
    } catch (error) {
      alert('Failed to generate referral code');
    } finally {
      setActionLoading(false);
    }
  };

  const copyReferralLink = () => {
    if (referralStats?.code) {
      const link = `${window.location.origin}/register?ref=${referralStats.code}`;
      navigator.clipboard.writeText(link);
      alert('Referral link copied to clipboard!');
    }
  };

  if (loading) {
    return (
      <>
        <RequireAuth />
        <div className="min-h-screen bg-gray-50 dark:bg-zinc-950 flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500 mx-auto mb-4"></div>
            <p className="text-gray-600 dark:text-gray-400">Loading account...</p>
          </div>
        </div>
      </>
    );
  }

  return (
    <>
      <RequireAuth />
      <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 py-8">
        <div className="max-w-6xl mx-auto px-4">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold mb-2 dark:text-white">💳 Account & Billing</h1>
            <p className="text-gray-600 dark:text-gray-300">
              Manage your subscription, billing, and referrals
            </p>
          </div>

          {/* Tabs */}
          <div className="flex gap-4 mb-6 border-b border-gray-200 dark:border-gray-700">
            <button
              onClick={() => setActiveTab('subscription')}
              className={`px-4 py-2 font-medium transition-colors border-b-2 ${
                activeTab === 'subscription'
                  ? 'border-indigo-600 text-indigo-600 dark:text-indigo-400'
                  : 'border-transparent text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-gray-200'
              }`}
            >
              💳 Subscription & Pricing
            </button>
            <button
              onClick={() => setActiveTab('referrals')}
              className={`px-4 py-2 font-medium transition-colors border-b-2 ${
                activeTab === 'referrals'
                  ? 'border-indigo-600 text-indigo-600 dark:text-indigo-400'
                  : 'border-transparent text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-gray-200'
              }`}
            >
              🎁 Referrals & Rewards
            </button>
          </div>

          {/* Subscription Tab */}
          {activeTab === 'subscription' && (
            <div className="space-y-6">
              {/* Current Subscription */}
              <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6 shadow-sm">
                <h2 className="text-xl font-semibold mb-4 dark:text-white">Current Plan</h2>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-2xl font-bold capitalize dark:text-white">{subscription?.tier || 'Free'}</p>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      Status: <span className="capitalize">{subscription?.status || 'Active'}</span>
                    </p>
                    {subscription?.current_period_end && (
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        {subscription.cancel_at_period_end ? 'Cancels' : 'Renews'} on{' '}
                        {new Date(subscription.current_period_end).toLocaleDateString()}
                      </p>
                    )}
                  </div>
                  {subscription?.tier !== 'free' && (
                    <button
                      className="px-4 py-2 text-sm text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-gray-200 border rounded-lg"
                      onClick={() => alert('Manage billing via Stripe Customer Portal (to be implemented)')}
                    >
                      Manage Billing
                    </button>
                  )}
                </div>
              </div>

              {/* Pricing Plans */}
              <div>
                <h2 className="text-xl font-semibold mb-4 dark:text-white">Available Plans</h2>
                <div className="grid md:grid-cols-3 gap-6">
                  {pricingTiers.map((tier) => (
                    <div
                      key={tier.id}
                      className={`relative bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6 shadow-sm ${
                        tier.popular ? 'ring-2 ring-indigo-600' : ''
                      }`}
                    >
                      {tier.popular && (
                        <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-indigo-600 text-white px-3 py-1 rounded-full text-xs font-semibold">
                          Most Popular
                        </div>
                      )}
                      <div className="mb-4">
                        <h3 className="text-xl font-bold dark:text-white">{tier.name}</h3>
                        <div className="mt-2">
                          {tier.price === 0 ? (
                            <span className="text-3xl font-bold dark:text-white">Free</span>
                          ) : (
                            <>
                              <span className="text-3xl font-bold dark:text-white">${(tier.price! / 100).toFixed(0)}</span>
                              <span className="text-gray-600 dark:text-gray-400">/{tier.interval}</span>
                            </>
                          )}
                        </div>
                      </div>
                      <ul className="space-y-2 mb-6">
                        {tier.features.map((feature, idx) => (
                          <li key={idx} className="flex items-start gap-2 text-sm">
                            <span className="text-green-500 mt-0.5">✓</span>
                            <span className="dark:text-gray-300">{feature}</span>
                          </li>
                        ))}
                      </ul>
                      <button
                        onClick={() => handleUpgrade(tier.id)}
                        disabled={subscription?.tier === tier.id || actionLoading}
                        className={`w-full py-2 rounded-lg font-medium transition ${
                          subscription?.tier === tier.id
                            ? 'bg-gray-200 dark:bg-zinc-800 text-gray-600 dark:text-gray-400 cursor-not-allowed'
                            : tier.popular
                            ? 'bg-indigo-600 text-white hover:bg-indigo-700'
                            : 'bg-gray-100 dark:bg-zinc-800 hover:bg-gray-200 dark:hover:bg-zinc-700'
                        }`}
                      >
                        {subscription?.tier === tier.id
                          ? 'Current Plan'
                          : tier.id === 'free'
                          ? 'Downgrade'
                          : subscription?.tier === 'free'
                          ? 'Start 14-day Trial'
                          : 'Upgrade'}
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Referrals Tab */}
          {activeTab === 'referrals' && (
            <div className="space-y-6">
              {/* Referral Code */}
              <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6 shadow-sm">
                <h2 className="text-xl font-semibold mb-4 dark:text-white">Your Referral Code</h2>
                {referralStats?.code ? (
                  <div className="space-y-4">
                    <div className="flex items-center gap-4">
                      <div className="flex-1 bg-gray-100 dark:bg-gray-700 rounded-lg p-4 font-mono text-lg dark:text-white">
                        {referralStats.code}
                      </div>
                      <button
                        onClick={copyReferralLink}
                        className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
                      >
                        Copy Link
                      </button>
                    </div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      Share this link with friends. When they sign up using your link, you both get rewards!
                    </p>
                    <div className="text-sm text-gray-600 dark:text-gray-400">
                      <p><strong>How it works:</strong></p>
                      <ol className="list-decimal list-inside space-y-1 mt-2">
                        <li>Share your referral link with friends</li>
                        <li>They click the link and register for an account</li>
                        <li>Once they complete their first lesson, you both get rewards</li>
                        <li>Earn bonus XP, coins, and unlock exclusive features</li>
                      </ol>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <p className="text-gray-600 dark:text-gray-400 mb-4">
                      You don't have a referral code yet
                    </p>
                    <button
                      onClick={generateReferralCode}
                      disabled={actionLoading}
                      className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50"
                    >
                      {actionLoading ? 'Generating...' : 'Generate Referral Code'}
                    </button>
                  </div>
                )}
              </div>

              {/* Referral Stats */}
              {referralStats && (
                <div className="grid md:grid-cols-4 gap-4">
                  <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4 shadow-sm">
                    <p className="text-sm text-gray-600 dark:text-gray-400">Total Referrals</p>
                    <p className="text-2xl font-bold">{referralStats.total_referrals}</p>
                  </div>
                  <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4 shadow-sm">
                    <p className="text-sm text-gray-600 dark:text-gray-400">Successful</p>
                    <p className="text-2xl font-bold text-green-600">{referralStats.successful_referrals}</p>
                  </div>
                  <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4 shadow-sm">
                    <p className="text-sm text-gray-600 dark:text-gray-400">Pending</p>
                    <p className="text-2xl font-bold text-yellow-600">{referralStats.pending_referrals}</p>
                  </div>
                  <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-4 shadow-sm">
                    <p className="text-sm text-gray-600 dark:text-gray-400">Total Rewards</p>
                    <p className="text-2xl font-bold text-indigo-600">{referralStats.total_rewards} XP</p>
                  </div>
                </div>
              )}

              {/* Rewards Info */}
              <div className="bg-gradient-to-r from-indigo-50 to-purple-50 dark:from-indigo-900/20 dark:to-purple-900/20 rounded-lg border p-6">
                <h3 className="text-lg font-semibold mb-3">🎁 Referral Rewards</h3>
                <div className="space-y-2 text-sm">
                  <p>• <strong>100 XP</strong> for each successful referral</p>
                  <p>• <strong>50 Coins</strong> when your friend completes their first lesson</p>
                  <p>• <strong>Bonus rewards</strong> for every 5 successful referrals</p>
                  <p>• <strong>Exclusive badges</strong> for top referrers</p>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </>
  );
}
