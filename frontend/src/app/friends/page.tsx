'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import RequireAuth from '@/components/RequireAuth';

interface Friend {
  user_id: string;
  email: string;
  name?: string;
  level: number;
  total_xp: number;
  current_streak: number;
  friends_since: string;
}

interface FriendRequest {
  request_id: string;
  from_user_id?: string;
  to_user_id?: string;
  from_email?: string;
  to_email?: string;
  from_name?: string;
  to_name?: string;
  created_at: string;
}

interface SearchResult {
  user_id: string;
  email: string;
  name?: string;
  level: number;
  total_xp?: number;
  is_friend: boolean;
  request_pending: boolean;
}

export default function FriendsPage() {
  const router = useRouter();
  const [friends, setFriends] = useState<Friend[]>([]);
  const [incomingRequests, setIncomingRequests] = useState<FriendRequest[]>([]);
  const [outgoingRequests, setOutgoingRequests] = useState<FriendRequest[]>([]);
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [activeTab, setActiveTab] = useState<'friends' | 'requests' | 'search'>('friends');
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState<string | null>(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/login');
      return;
    }

    try {
      const [friendsRes, incomingRes, outgoingRes] = await Promise.all([
        fetch('http://localhost:8000/api/v1/friends/list', {
          headers: { 'Authorization': `Bearer ${token}` }
        }),
        fetch('http://localhost:8000/api/v1/friends/requests/incoming', {
          headers: { 'Authorization': `Bearer ${token}` }
        }),
        fetch('http://localhost:8000/api/v1/friends/requests/outgoing', {
          headers: { 'Authorization': `Bearer ${token}` }
        })
      ]);

      if (friendsRes.ok) setFriends(await friendsRes.json());
      if (incomingRes.ok) setIncomingRequests(await incomingRes.json());
      if (outgoingRes.ok) setOutgoingRequests(await outgoingRes.json());

      setLoading(false);
    } catch (err) {
      console.error('Failed to load friends data:', err);
      setLoading(false);
    }
  };

  const searchUsers = async () => {
    if (!searchQuery.trim()) return;

    const token = localStorage.getItem('token');
    try {
      const res = await fetch(`http://localhost:8000/api/v1/friends/search?query=${encodeURIComponent(searchQuery)}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        setSearchResults(await res.json());
        setActiveTab('search');
      }
    } catch (err) {
      console.error('Failed to search users:', err);
    }
  };

  const sendFriendRequest = async (userId: string) => {
    setActionLoading(userId);
    const token = localStorage.getItem('token');
    try {
      const res = await fetch('http://localhost:8000/api/v1/friends/request', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ to_user_id: userId })
      });

      if (res.ok) {
        alert('Friend request sent!');
        await fetchData();
        await searchUsers(); // Refresh search results
      } else {
        const error = await res.json();
        alert(error.detail || 'Failed to send friend request');
      }
    } catch (err) {
      console.error('Failed to send friend request:', err);
      alert('Failed to send friend request');
    } finally {
      setActionLoading(null);
    }
  };

  const respondToRequest = async (requestId: string, accept: boolean) => {
    setActionLoading(requestId);
    const token = localStorage.getItem('token');
    try {
      const res = await fetch('http://localhost:8000/api/v1/friends/request/respond', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ request_id: requestId, accept })
      });

      if (res.ok) {
        alert(accept ? 'Friend request accepted!' : 'Friend request declined');
        await fetchData();
      }
    } catch (err) {
      console.error('Failed to respond to request:', err);
    } finally {
      setActionLoading(null);
    }
  };

  const removeFriend = async (userId: string) => {
    if (!confirm('Are you sure you want to remove this friend?')) return;

    setActionLoading(userId);
    const token = localStorage.getItem('token');
    try {
      const res = await fetch(`http://localhost:8000/api/v1/friends/remove/${userId}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (res.ok) {
        alert('Friend removed');
        await fetchData();
      }
    } catch (err) {
      console.error('Failed to remove friend:', err);
    } finally {
      setActionLoading(null);
    }
  };

  if (loading) {
    return (
      <>
        <RequireAuth />
        <div className="min-h-screen bg-gray-50 dark:bg-zinc-950 flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500 mx-auto mb-4"></div>
            <p className="text-gray-600 dark:text-gray-400">Loading friends...</p>
          </div>
        </div>
      </>
    );
  }

  return (
    <>
      <RequireAuth />
      <div className="min-h-screen bg-gray-50 dark:bg-zinc-950 py-8">
        <div className="max-w-6xl mx-auto px-4">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold mb-2">👥 Friends & Social</h1>
            <p className="text-gray-600 dark:text-gray-400">
              Connect with other learners, compete on leaderboards, and motivate each other
            </p>
          </div>

          {/* Info Banner */}
          <div className="bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-lg border p-4 mb-6">
            <h3 className="font-semibold mb-2">💡 How Friends Work</h3>
            <ul className="text-sm space-y-1 text-gray-700 dark:text-gray-300">
              <li>• <strong>Search</strong> for users by email to send friend requests</li>
              <li>• <strong>Accept</strong> incoming requests to add them as friends</li>
              <li>• <strong>Compete</strong> with friends on leaderboards and challenges</li>
              <li>• <strong>Track</strong> each other's progress, streaks, and achievements</li>
              <li>• <strong>Motivate</strong> each other to maintain daily streaks</li>
            </ul>
          </div>

          {/* Search Bar */}
          <div className="mb-6">
            <div className="flex gap-2">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && searchUsers()}
                placeholder="Search users by email..."
                className="flex-1 px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:bg-zinc-800 dark:border-zinc-700"
              />
              <button
                onClick={searchUsers}
                className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
              >
                Search
              </button>
            </div>
          </div>

          {/* Tabs */}
          <div className="flex gap-4 mb-6 border-b border-gray-200 dark:border-zinc-800">
            <button
              onClick={() => setActiveTab('friends')}
              className={`px-4 py-2 font-medium transition-colors border-b-2 ${
                activeTab === 'friends'
                  ? 'border-indigo-600 text-indigo-600'
                  : 'border-transparent text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-gray-200'
              }`}
            >
              Friends ({friends.length})
            </button>
            <button
              onClick={() => setActiveTab('requests')}
              className={`px-4 py-2 font-medium transition-colors border-b-2 relative ${
                activeTab === 'requests'
                  ? 'border-indigo-600 text-indigo-600'
                  : 'border-transparent text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-gray-200'
              }`}
            >
              Requests ({incomingRequests.length + outgoingRequests.length})
              {incomingRequests.length > 0 && (
                <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center">
                  {incomingRequests.length}
                </span>
              )}
            </button>
            <button
              onClick={() => setActiveTab('search')}
              className={`px-4 py-2 font-medium transition-colors border-b-2 ${
                activeTab === 'search'
                  ? 'border-indigo-600 text-indigo-600'
                  : 'border-transparent text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-gray-200'
              }`}
            >
              Search Results ({searchResults.length})
            </button>
          </div>

          {/* Friends Tab */}
          {activeTab === 'friends' && (
            <div className="space-y-4">
              {friends.length === 0 ? (
                <div className="text-center py-12 bg-white dark:bg-zinc-900 rounded-lg border">
                  <div className="text-6xl mb-4">👥</div>
                  <h3 className="text-xl font-semibold mb-2">No friends yet</h3>
                  <p className="text-gray-600 dark:text-gray-400 mb-4">
                    Search for users by email and send friend requests
                  </p>
                </div>
              ) : (
                friends.map((friend) => (
                  <div key={friend.user_id} className="bg-white dark:bg-zinc-900 rounded-lg border p-4 flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <div className="h-12 w-12 rounded-full bg-indigo-100 dark:bg-indigo-900 flex items-center justify-center">
                        <span className="text-xl font-bold text-indigo-600">
                          {(friend.name || friend.email).charAt(0).toUpperCase()}
                        </span>
                      </div>
                      <div>
                        <p className="font-semibold">{friend.name || friend.email}</p>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          Level {friend.level} • {friend.total_xp} XP • {friend.current_streak} day streak
                        </p>
                        <p className="text-xs text-gray-500">
                          Friends since {new Date(friend.friends_since).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                    <button
                      onClick={() => removeFriend(friend.user_id)}
                      disabled={actionLoading === friend.user_id}
                      className="px-4 py-2 text-sm text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg disabled:opacity-50"
                    >
                      Remove
                    </button>
                  </div>
                ))
              )}
            </div>
          )}

          {/* Requests Tab */}
          {activeTab === 'requests' && (
            <div className="space-y-6">
              {/* Incoming Requests */}
              <div>
                <h3 className="text-lg font-semibold mb-3">Incoming Requests</h3>
                {incomingRequests.length === 0 ? (
                  <p className="text-gray-600 dark:text-gray-400 text-center py-8 bg-white dark:bg-zinc-900 rounded-lg border">
                    No incoming requests
                  </p>
                ) : (
                  <div className="space-y-3">
                    {incomingRequests.map((request) => (
                      <div key={request.request_id} className="bg-white dark:bg-zinc-900 rounded-lg border p-4 flex items-center justify-between">
                        <div>
                          <p className="font-semibold">{request.from_name || request.from_email}</p>
                          <p className="text-sm text-gray-600 dark:text-gray-400">
                            Sent {new Date(request.created_at).toLocaleDateString()}
                          </p>
                        </div>
                        <div className="flex gap-2">
                          <button
                            onClick={() => respondToRequest(request.request_id, true)}
                            disabled={actionLoading === request.request_id}
                            className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
                          >
                            Accept
                          </button>
                          <button
                            onClick={() => respondToRequest(request.request_id, false)}
                            disabled={actionLoading === request.request_id}
                            className="px-4 py-2 bg-gray-200 dark:bg-zinc-800 rounded-lg hover:bg-gray-300 dark:hover:bg-zinc-700 disabled:opacity-50"
                          >
                            Decline
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Outgoing Requests */}
              <div>
                <h3 className="text-lg font-semibold mb-3">Outgoing Requests</h3>
                {outgoingRequests.length === 0 ? (
                  <p className="text-gray-600 dark:text-gray-400 text-center py-8 bg-white dark:bg-zinc-900 rounded-lg border">
                    No outgoing requests
                  </p>
                ) : (
                  <div className="space-y-3">
                    {outgoingRequests.map((request) => (
                      <div key={request.request_id} className="bg-white dark:bg-zinc-900 rounded-lg border p-4 flex items-center justify-between">
                        <div>
                          <p className="font-semibold">{request.to_name || request.to_email}</p>
                          <p className="text-sm text-gray-600 dark:text-gray-400">
                            Sent {new Date(request.created_at).toLocaleDateString()}
                          </p>
                        </div>
                        <span className="text-sm text-yellow-600 dark:text-yellow-400">Pending</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Search Results Tab */}
          {activeTab === 'search' && (
            <div className="space-y-4">
              {searchResults.length === 0 ? (
                <div className="text-center py-12 bg-white dark:bg-zinc-900 rounded-lg border">
                  <div className="text-6xl mb-4">🔍</div>
                  <h3 className="text-xl font-semibold mb-2">No results</h3>
                  <p className="text-gray-600 dark:text-gray-400">
                    Try searching by email address
                  </p>
                </div>
              ) : (
                searchResults.map((user) => (
                  <div key={user.user_id} className="bg-white dark:bg-zinc-900 rounded-lg border p-4 flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <div className="h-12 w-12 rounded-full bg-indigo-100 dark:bg-indigo-900 flex items-center justify-center">
                        <span className="text-xl font-bold text-indigo-600">
                          {(user.name || user.email).charAt(0).toUpperCase()}
                        </span>
                      </div>
                      <div>
                        <p className="font-semibold">{user.name || user.email}</p>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          Level {user.level} {user.total_xp && `• ${user.total_xp} XP`}
                        </p>
                      </div>
                    </div>
                    <div>
                      {user.is_friend ? (
                        <span className="px-4 py-2 bg-green-100 dark:bg-green-900/20 text-green-700 dark:text-green-400 rounded-lg text-sm">
                          ✓ Friends
                        </span>
                      ) : user.request_pending ? (
                        <span className="px-4 py-2 bg-yellow-100 dark:bg-yellow-900/20 text-yellow-700 dark:text-yellow-400 rounded-lg text-sm">
                          Pending
                        </span>
                      ) : (
                        <button
                          onClick={() => sendFriendRequest(user.user_id)}
                          disabled={actionLoading === user.user_id}
                          className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50"
                        >
                          Add Friend
                        </button>
                      )}
                    </div>
                  </div>
                ))
              )}
            </div>
          )}
        </div>
      </div>
    </>
  );
}
