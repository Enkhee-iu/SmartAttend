'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { FaceCamera } from '@/components/FaceCamera';

export default function RegisterPage() {
  const router = useRouter();
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [role, setRole] = useState<'STUDENT' | 'TEACHER'>('STUDENT');
  const [faceImage, setFaceImage] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [step, setStep] = useState<1 | 2>(1);
  const [userId, setUserId] = useState<string | null>(null);

  // Step 1: Register with email
  const handleEmailRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      // Create user first
      const createUserResponse = await fetch('/api/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name,
          email,
          role,
        }),
      });

      const userData = await createUserResponse.json();

      if (!createUserResponse.ok || !userData.success) {
        throw new Error(userData.error || 'Registration failed');
      }

      // Save userId and move to face registration step
      setUserId(userData.userId);
      setStep(2);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  // Step 2: Register face
  const handleFaceCapture = async (imageData: string) => {
    if (!userId) {
      setError('User ID not found. Please start over.');
      return;
    }

    setLoading(true);
    setError(null);
    setFaceImage(imageData);

    try {
      // Register face
      const faceResponse = await fetch('/api/ai/face', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: 'register',
          userId: userId,
          image: imageData,
        }),
      });

      const faceData = await faceResponse.json();

      if (!faceResponse.ok || !faceData.success) {
        throw new Error(faceData.error || 'Face registration failed');
      }

      // Face registered successfully, create session and redirect to dashboard
      const loginResponse = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          method: 'face',
          image: imageData,
        }),
      });

      const loginData = await loginResponse.json();

      if (loginResponse.ok && loginData.success && loginData.token) {
        localStorage.setItem('auth_token', loginData.token);
        router.push('/dashboard');
      } else {
        // If face login fails, redirect to login page
        router.push('/login?registered=true');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Face registration failed');
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        {/* Back to Home Button */}
        <div className="text-left">
          <Link
            href="/"
            className="inline-flex items-center text-sm text-gray-600 hover:text-gray-900 transition-colors"
          >
            <svg
              className="w-4 h-4 mr-2"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M10 19l-7-7m0 0l7-7m-7 7h18"
              />
            </svg>
            Нүүр хуудас руу буцах
          </Link>
        </div>

        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Бүртгүүлэх
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Шинэ хэрэглэгч бүртгүүлэх
          </p>
        </div>

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        )}

        {step === 1 && (
          <form className="mt-8 space-y-6" onSubmit={handleEmailRegister}>
            <div>
              <label htmlFor="name" className="block text-sm font-medium text-gray-700">
                Нэр
              </label>
              <input
                id="name"
                name="name"
                type="text"
                required
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="mt-1 appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                placeholder="Таны нэр"
                disabled={loading}
              />
            </div>

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
                disabled={loading}
              />
            </div>

            <div>
              <label htmlFor="role" className="block text-sm font-medium text-gray-700">
                Эрх
              </label>
              <select
                id="role"
                name="role"
                value={role}
                onChange={(e) => setRole(e.target.value as 'STUDENT' | 'TEACHER')}
                className="mt-1 block w-full px-3 py-2 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                disabled={loading}
              >
                <option value="STUDENT">Оюутан</option>
                <option value="TEACHER">Багш</option>
              </select>
            </div>

            <div>
              <button
                type="submit"
                disabled={loading}
                className="w-full py-2 px-4 border border-transparent rounded-md text-white bg-blue-600 hover:bg-blue-700 disabled:opacity-50"
              >
                {loading ? 'Бүртгэж байна...' : 'Дараагийн алхам'}
              </button>
            </div>
          </form>
        )}

        {step === 2 && (
          <div className="mt-8">
            <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-lg">
              <p className="text-sm text-green-800">
                ✅ <strong>{name}</strong> бүртгэл амжилттай!
              </p>
              <p className="text-sm text-green-700 mt-1">
                Одоо нүүрний зургаа бүртгэх хэрэгтэй
              </p>
            </div>
            
            <p className="text-center text-gray-600 mb-6">
              Нүүрний зургаа авах
            </p>
            <FaceCamera onCapture={handleFaceCapture} onError={setError} />
            {loading && (
              <p className="mt-4 text-center text-blue-600">
                Нүүр бүртгэж байна...
              </p>
            )}
            
            <div className="mt-4 text-center">
              <button
                type="button"
                onClick={() => {
                  setStep(1);
                  setFaceImage(null);
                  setError(null);
                }}
                disabled={loading}
                className="text-sm text-gray-600 hover:text-gray-800 disabled:opacity-50"
              >
                Буцах
              </button>
            </div>
          </div>
        )}

        <div className="text-center">
          <a href="/login" className="text-sm text-blue-600 hover:text-blue-500">
            Аль хэдийн бүртгэлтэй? Нэвтрэх
          </a>
        </div>
      </div>
    </div>
  );
}
