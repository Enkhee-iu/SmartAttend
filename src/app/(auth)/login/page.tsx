'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { FaceCamera } from '@/components/FaceCamera';

export default function LoginPage() {
  const router = useRouter();
  const [method, setMethod] = useState<'face' | 'passwordless'>('face');
  const [email, setEmail] = useState('');
  const [code, setCode] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [codeSent, setCodeSent] = useState(false);

  const handleFaceCapture = async (imageData: string) => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          method: 'face',
          image: imageData,
        }),
      });

      const data = await response.json();

      if (!response.ok || !data.success) {
        throw new Error(data.error || 'Authentication failed');
      }

      // Store token
      if (data.token) {
        localStorage.setItem('auth_token', data.token);
      }

      // Redirect to dashboard
      router.push('/dashboard');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Authentication failed');
      setLoading(false);
    }
  };

  const handlePasswordlessInitiate = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          method: 'passwordless',
          email,
        }),
      });

      const data = await response.json();

      if (!response.ok || !data.success) {
        throw new Error(data.error || 'Failed to send code');
      }

      setCodeSent(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to initiate authentication');
    } finally {
      setLoading(false);
    }
  };

  const handlePasswordlessVerify = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          method: 'passwordless',
          email,
          code,
        }),
      });

      const data = await response.json();

      if (!response.ok || !data.success) {
        throw new Error(data.error || 'Invalid code');
      }

      // Store token
      if (data.token) {
        localStorage.setItem('auth_token', data.token);
      }

      // Redirect to dashboard
      router.push('/dashboard');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Verification failed');
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Нэвтрэх
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            AI таних системд нэвтрэх
          </p>
        </div>

        <div className="flex justify-center space-x-4 mb-6">
          <button
            onClick={() => {
              setMethod('face');
              setCodeSent(false);
              setError(null);
            }}
            className={`px-4 py-2 rounded-lg ${
              method === 'face'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-700'
            }`}
          >
            Нүүр таних
          </button>
          <button
            onClick={() => {
              setMethod('passwordless');
              setCodeSent(false);
              setError(null);
            }}
            className={`px-4 py-2 rounded-lg ${
              method === 'passwordless'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-700'
            }`}
          >
            Нууц үггүй
          </button>
        </div>

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        )}

        {method === 'face' && (
          <div className="mt-8">
            <FaceCamera onCapture={handleFaceCapture} onError={setError} />
            {loading && (
              <p className="mt-4 text-center text-gray-600">Таних үед...</p>
            )}
          </div>
        )}

        {method === 'passwordless' && (
          <form
            className="mt-8 space-y-6"
            onSubmit={codeSent ? handlePasswordlessVerify : handlePasswordlessInitiate}
          >
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                Имэйл
              </label>
              <input
                id="email"
                name="email"
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="mt-1 appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                placeholder="name@example.com"
                disabled={codeSent || loading}
              />
            </div>

            {codeSent && (
              <div>
                <label htmlFor="code" className="block text-sm font-medium text-gray-700">
                  Код
                </label>
                <input
                  id="code"
                  name="code"
                  type="text"
                  required
                  value={code}
                  onChange={(e) => setCode(e.target.value)}
                  className="mt-1 appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                  placeholder="6 оронтой код"
                  maxLength={6}
                  disabled={loading}
                />
              </div>
            )}

            <div>
              <button
                type="submit"
                disabled={loading}
                className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
              >
                {loading
                  ? 'Хүлээж байна...'
                  : codeSent
                    ? 'Баталгаажуулах'
                    : 'Код илгээх'}
              </button>
            </div>
          </form>
        )}

        <div className="text-center">
          <a href="/register" className="text-sm text-blue-600 hover:text-blue-500">
            Бүртгүүлэх
          </a>
        </div>
      </div>
    </div>
  );
}
