'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { FaceCamera } from '@/components/FaceCamera';
import { Chatbot } from '@/components/Chatbot';

interface Attendance {
  id: string;
  type: string;
  recognizedBy: string;
  timestamp: string;
  location?: string;
}

interface User {
  id: string;
  name: string;
  email: string;
  role: string;
}

export default function DashboardPage() {
  const router = useRouter();
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [attendances, setAttendances] = useState<Attendance[]>([]);
  const [showCamera, setShowCamera] = useState(false);
  const [recording, setRecording] = useState(false);

  useEffect(() => {
    checkAuth();
    loadAttendances();
  }, []);

  const checkAuth = async () => {
    const token = localStorage.getItem('auth_token');
    if (!token) {
      router.push('/login');
      return;
    }

    try {
      const response = await fetch('/api/auth/login', {
        headers: { 'Authorization': `Bearer ${token}` },
      });

      const data = await response.json();
      if (!data.authenticated) {
        localStorage.removeItem('auth_token');
        router.push('/login');
        return;
      }

      setUser(data.user);
    } catch (error) {
      console.error('Auth check error:', error);
      router.push('/login');
    } finally {
      setLoading(false);
    }
  };

  const loadAttendances = async () => {
    const token = localStorage.getItem('auth_token');
    if (!token) return;

    try {
      const response = await fetch('/api/attendance', {
        headers: { 'Authorization': `Bearer ${token}` },
      });

      const data = await response.json();
      if (data.success) {
        setAttendances(data.attendances || []);
      }
    } catch (error) {
      console.error('Load attendances error:', error);
    }
  };

  const handleFaceCapture = async (imageData: string) => {
    setRecording(true);
    const token = localStorage.getItem('auth_token');

    try {
      // Face recognition + автомат бүртгэл
      const recognizeResponse = await fetch('/api/ai/face', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          image: imageData,
          autoRegister: true, // Автомат бүртгэл идэвхжүүлэх
          location: 'Dashboard',
          // course: 'Хичээлийн нэр', // Хэрэв хэрэгтэй бол
        }),
      });

      const recognizeData = await recognizeResponse.json();

      if (!recognizeData.success || !recognizeData.userId) {
        alert('Нүүр танигдаагүй байна. Дахин оролдоно уу.');
        setRecording(false);
        return;
      }

      // Давхардсан бүртгэл шалгах
      if (recognizeData.isDuplicate) {
        alert('Та энэ өдөр/цагт аль хэдийн бүртгэгдсэн байна. Давхардсан бүртгэл.');
        setShowCamera(false);
        loadAttendances();
        return;
      }

      // Автомат бүртгэл амжилттай
      if (recognizeData.attendance) {
        alert('Бүртгэл амжилттай хийгдлээ!');
        setShowCamera(false);
        loadAttendances();
      } else {
        // Хэрэв attendance үүсгэгдээгүй бол (алдаа гарсан)
        alert('Бүртгэл үүсгэхэд алдаа гарлаа. Дахин оролдоно уу.');
      }
    } catch (error) {
      console.error('Attendance recording error:', error);
      alert('Алдаа гарлаа. Дахин оролдоно уу.');
    } finally {
      setRecording(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('auth_token');
    router.push('/login');
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-lg text-gray-600">Уншиж байна...</p>
      </div>
    );
  }

  if (!user) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">SmartAttend</h1>
              <p className="text-sm text-gray-600">
                Сайн байна уу, {user.name}
              </p>
            </div>
            <button
              onClick={handleLogout}
              className="px-4 py-2 text-sm text-red-600 hover:text-red-700 hover:bg-red-50 rounded-lg transition-colors"
            >
              Гарах
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Quick Actions */}
        <div className="mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Хурдан үйлдлүүд</h2>
          <div className="flex gap-4">
            <button
              onClick={() => setShowCamera(!showCamera)}
              disabled={recording}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed font-medium"
            >
              {showCamera ? 'Хаах' : 'Бүртгэл Хийх'}
            </button>
          </div>
        </div>

        {/* Camera Section */}
        {showCamera && (
          <div className="mb-8 bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Нүүрний зургаа авах
            </h3>
            <FaceCamera
              onCapture={handleFaceCapture}
              onError={(error) => {
                alert('Камерын алдаа: ' + error);
                setShowCamera(false);
              }}
            />
            {recording && (
              <div className="mt-4 text-center">
                <p className="text-blue-600">Бүртгэл хийж байна...</p>
              </div>
            )}
          </div>
        )}

        {/* Statistics */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-sm font-medium text-gray-500 mb-2">Нийт Бүртгэл</h3>
            <p className="text-3xl font-bold text-gray-900">{attendances.length}</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-sm font-medium text-gray-500 mb-2">Ирсэн</h3>
            <p className="text-3xl font-bold text-green-600">
              {attendances.filter((a) => a.type === 'PRESENT').length}
            </p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-sm font-medium text-gray-500 mb-2">Хоцорсон</h3>
            <p className="text-3xl font-bold text-yellow-600">
              {attendances.filter((a) => a.type === 'LATE').length}
            </p>
          </div>
        </div>

        {/* Attendance History */}
        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          <div className="px-6 py-4 border-b">
            <h2 className="text-xl font-semibold text-gray-900">Бүртгэлийн Түүх</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Огноо
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Төрөл
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Танилт
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Байршил
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {attendances.length === 0 ? (
                  <tr>
                    <td colSpan={4} className="px-6 py-4 text-center text-gray-500">
                      Бүртгэл байхгүй байна
                    </td>
                  </tr>
                ) : (
                  attendances.map((attendance) => (
                    <tr key={attendance.id}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {new Date(attendance.timestamp).toLocaleString('mn-MN')}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span
                          className={`px-2 py-1 text-xs font-semibold rounded-full ${
                            attendance.type === 'PRESENT'
                              ? 'bg-green-100 text-green-800'
                              : attendance.type === 'LATE'
                                ? 'bg-yellow-100 text-yellow-800'
                                : 'bg-red-100 text-red-800'
                          }`}
                        >
                          {attendance.type === 'PRESENT'
                            ? 'Ирсэн'
                            : attendance.type === 'LATE'
                              ? 'Хоцорсон'
                              : attendance.type}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {attendance.recognizedBy === 'FACE' ? 'Нүүр' : attendance.recognizedBy}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {attendance.location || '-'}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </main>
      
      {/* Chatbot */}
      <Chatbot />
    </div>
  );
}
