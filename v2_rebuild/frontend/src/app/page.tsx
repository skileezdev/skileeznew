import Link from "next/link";
import Image from "next/image";

export default function Home() {
  return (
    <div className="min-h-screen bg-slate-50 overflow-hidden">
      {/* Navigation */}
      <nav className="fixed top-0 w-full z-50 bg-white/80 backdrop-blur-md border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold">S</span>
            </div>
            <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-indigo-600">
              Skileez V2
            </span>
          </div>
          <div className="hidden md:flex items-center gap-8 text-sm font-medium text-slate-600">
            <Link href="/marketplace" className="hover:text-blue-600 transition-colors">Marketplace</Link>
            <Link href="/auth/login" className="hover:text-blue-600 transition-colors">Login</Link>
            <Link
              href="/auth/signup"
              className="bg-blue-600 text-white px-5 py-2 rounded-full hover:bg-blue-700 transition-all shadow-lg shadow-blue-200"
            >
              Get Started
            </Link>
          </div>
        </div>
      </nav>

      <main>
        {/* Hero Section */}
        <section className="relative pt-32 pb-20 lg:pt-48 lg:pb-32 overflow-hidden">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
            <div className="text-center">
              <h1 className="text-5xl lg:text-7xl font-extrabold tracking-tight text-slate-900 mb-6">
                Master New Skills with <br />
                <span className="text-blue-600">Expert Coaching</span>
              </h1>
              <p className="text-xl text-slate-600 max-w-2xl mx-auto mb-10 leading-relaxed">
                Skileez connects ambitious learners with specialized coaches for 1-on-1 sessions.
                Fast, flexible, and built for your growth.
              </p>
              <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                <Link
                  href="/auth/signup"
                  className="w-full sm:w-auto px-8 py-4 bg-blue-600 text-white rounded-2xl font-bold text-lg hover:bg-blue-700 transition-all shadow-xl shadow-blue-200 transform hover:-translate-y-1"
                >
                  Join as Student
                </Link>
                <Link
                  href="/auth/signup"
                  className="w-full sm:w-auto px-8 py-4 bg-white text-slate-900 border-2 border-slate-200 rounded-2xl font-bold text-lg hover:border-blue-600 hover:text-blue-600 transition-all transform hover:-translate-y-1"
                >
                  Apply as Coach
                </Link>
              </div>
            </div>
          </div>

          {/* Background Decorative Elements */}
          <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-full -z-0 pointer-events-none">
            <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-blue-400/10 rounded-full blur-[120px]" />
            <div className="absolute bottom-[10%] right-[-10%] w-[40%] h-[40%] bg-indigo-400/10 rounded-full blur-[120px]" />
          </div>
        </section>

        {/* Feature Grid */}
        <section className="py-20 bg-white">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-12 text-center">
              <div className="p-8 rounded-3xl bg-slate-50 border border-slate-100">
                <div className="w-12 h-12 bg-blue-100 text-blue-600 rounded-xl flex items-center justify-center mx-auto mb-6 text-2xl">⚡</div>
                <h3 className="text-xl font-bold mb-4">Fast Matching</h3>
                <p className="text-slate-600">Post a request and get expert proposals in minutes.</p>
              </div>
              <div className="p-8 rounded-3xl bg-slate-50 border border-slate-100">
                <div className="w-12 h-12 bg-indigo-100 text-indigo-600 rounded-xl flex items-center justify-center mx-auto mb-6 text-2xl">🔒</div>
                <h3 className="text-xl font-bold mb-4">Secure Contracts</h3>
                <p className="text-slate-600">Built-in agreements to protect both students and coaches.</p>
              </div>
              <div className="p-8 rounded-3xl bg-slate-50 border border-slate-100">
                <div className="w-12 h-12 bg-emerald-100 text-emerald-600 rounded-xl flex items-center justify-center mx-auto mb-6 text-2xl">📹</div>
                <h3 className="text-xl font-bold mb-4">Integrated Video</h3>
                <p className="text-slate-600">HD Video workspace built directly into your dashboard.</p>
              </div>
            </div>
          </div>
        </section>
      </main>

      <footer className="py-12 border-t border-slate-200 text-center text-slate-500 text-sm">
        <p>© 2026 Skileez V2.0 - Rebuilt for the future of learning.</p>
      </footer>
    </div>
  );
}
