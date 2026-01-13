import Link from 'next/link';

export default function Home() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100 px-4">
      <main className="max-w-4xl w-full text-center">
        <h1 className="text-5xl font-bold text-gray-900 mb-4">
          SmartAttend
        </h1>
        <p className="text-xl text-gray-600 mb-8">
          AI-аар оюутны бүртгэл хийх ухаант систем
        </p>
        <p className="text-lg text-gray-500 mb-12">
          Нүүр таних технологи ашиглан автоматаар бүртгэл хийх, удирдах
        </p>
        
        <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
          <Link
            href="/login"
            className="px-8 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium text-lg"
          >
            Нэвтрэх
          </Link>
          <Link
            href="/register"
            className="px-8 py-3 bg-white text-blue-600 border-2 border-blue-600 rounded-lg hover:bg-blue-50 transition-colors font-medium text-lg"
          >
            Бүртгүүлэх
          </Link>
        </div>

        <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-6 text-left">
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-xl font-semibold mb-2 text-gray-900">🤖 AI Таних</h3>
            <p className="text-gray-600">
              Luxand Cloud AI ашиглан нүүрний таних технологи
            </p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-xl font-semibold mb-2 text-gray-900">⚡ Автомат</h3>
            <p className="text-gray-600">
              N8N automation ашиглан бүртгэлийн процесс автоматжуулах
            </p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h3 className="text-xl font-semibold mb-2 text-gray-900">📊 Тайлан</h3>
            <p className="text-gray-600">
              Бүртгэлийн түүх, статистик, тайлан үзэх боломж
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}
