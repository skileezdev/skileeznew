"use client";

import Link from "next/link";
import {
  Zap,
  ArrowRight,
  CheckCircle2,
  Star,
  Users,
  ShieldCheck,
  Sparkles,
  Globe,
  Award
} from "lucide-react";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-[#FDFDFF] text-gray-900 font-inter overflow-x-hidden">
      {/* Navigation (V1 Mirror) */}
      <nav className="fixed top-0 left-0 w-full z-[100] bg-white/80 backdrop-blur-xl border-b border-gray-100 px-8 py-5">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <div className="flex items-center gap-3 group cursor-pointer">
            <div className="w-10 h-10 bg-primary-600 rounded-xl flex items-center justify-center shadow-lg shadow-primary-200 group-hover:rotate-12 transition-transform">
              <Zap className="text-white fill-white" size={20} />
            </div>
            <span className="text-2xl font-black tracking-tighter text-gray-900">SKILEEZ<span className="text-primary-600">.</span></span>
          </div>

          <div className="hidden md:flex items-center gap-10 text-sm font-black uppercase tracking-widest text-gray-400">
            <a href="#features" className="hover:text-primary-600 transition-colors">Experience</a>
            <a href="#marketplace" className="hover:text-primary-600 transition-colors">Marketplace</a>
            <a href="#pricing" className="hover:text-primary-600 transition-colors">Pricing</a>
          </div>

          <div className="flex items-center gap-4">
            <Link href="/auth/login" className="px-6 py-3 text-sm font-black uppercase tracking-widest text-gray-500 hover:text-gray-900 transition-colors">
              Login
            </Link>
            <Link href="/auth/signup" className="px-8 py-3.5 bg-gray-900 text-white text-xs font-black uppercase tracking-widest rounded-2xl shadow-xl shadow-gray-200 hover:shadow-2xl hover:-translate-y-0.5 transition-all active:scale-95">
              Join the Elite
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section (Soul of V1) */}
      <header className="relative pt-48 pb-32 px-8 overflow-hidden">
        {/* Decorative Blobs */}
        <div className="absolute top-[-10%] right-[-10%] w-[50%] h-[50%] bg-primary-100/30 rounded-full blur-[120px] animate-pulse"></div>
        <div className="absolute bottom-[-10%] left-[-10%] w-[40%] h-[40%] bg-purple-100/30 rounded-full blur-[100px]"></div>

        <div className="max-w-7xl mx-auto text-center relative z-10">
          <div className="inline-flex items-center gap-2 px-6 py-2 bg-primary-50 text-primary-600 rounded-full text-[10px] font-black uppercase tracking-[0.2em] mb-8 animate-bounce">
            <Sparkles size={14} /> The Future of Mastery is Here
          </div>

          <h1 className="text-6xl md:text-8xl font-black tracking-tighter leading-[0.9] text-gray-900 mb-10 max-w-5xl mx-auto">
            Elevate Your Potential with <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary-600 to-purple-600">Expert Coaching.</span>
          </h1>

          <p className="text-xl md:text-2xl text-gray-400 font-medium max-w-3xl mx-auto leading-relaxed mb-16">
            Skileez connects ambitious learners with word-class instructors for hyper-personalized, results-driven educational experiences.
          </p>

          <div className="flex flex-col md:flex-row items-center justify-center gap-6">
            <Link href="/marketplace" className="group py-6 px-12 bg-primary-600 text-white font-black rounded-[2.5rem] shadow-2xl shadow-primary-200 hover:shadow-primary-300 hover:scale-105 active:scale-95 transition-all text-lg flex items-center gap-3">
              Explore Marketplace <ArrowRight className="group-hover:translate-x-1 transition-transform" />
            </Link>
            <Link href="/auth/signup" className="py-6 px-12 bg-white border-2 border-gray-100 text-gray-900 font-black rounded-[2.5rem] shadow-sm hover:shadow-xl hover:bg-gray-50 transition-all text-lg flex items-center gap-3">
              Become a Coach <Award size={24} />
            </Link>
          </div>

          <div className="mt-24 flex flex-wrap justify-center items-center gap-12 opacity-30 grayscale hover:opacity-100 hover:grayscale-0 transition-all duration-700">
            <p className="w-full text-center text-xs font-black uppercase tracking-[0.3em] mb-4 text-gray-400">Trusted by Learners Globally</p>
            <div className="flex items-center gap-2 text-2xl font-black">MASTERCLASS</div>
            <div className="flex items-center gap-2 text-2xl font-black tracking-widest italic">COURSERA</div>
            <div className="flex items-center gap-2 text-2xl font-black uppercase tracking-tighter">Skillshare</div>
            <div className="flex items-center gap-2 text-2xl font-black">Udemy</div>
          </div>
        </div>
      </header>

      {/* Feature Grid (1:1 V1 Logic) */}
      <section id="features" className="py-32 px-8 bg-white border-y border-gray-50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-24">
            <h2 className="text-4xl font-black text-gray-900 mb-4 tracking-tight">Engineered for Excellence.</h2>
            <p className="text-gray-400 font-bold max-w-xl mx-auto uppercase text-xs tracking-widest">A purpose-built platform for the modern educational exchange.</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-12">
            {[
              {
                icon: <ShieldCheck size={32} />,
                title: "Secure Agreements",
                desc: "Dynamic contracts protect both learners and coaches with automated state management and clear boundaries."
              },
              {
                icon: <Users size={32} />,
                title: "Curated Marketplace",
                desc: "Browse a verified ecosystem of expertise. From coding to creative arts, master anything with direct guidance."
              },
              {
                icon: <Globe size={32} />,
                title: "Global Access",
                desc: "Experience the Skileez soul from anywhere in the world with integrated video sessions and real-time scheduling."
              }
            ].map((item, i) => (
              <div key={i} className="group p-10 rounded-[3rem] bg-[#FDFDFF] border border-gray-50 hover:border-primary-100 hover:shadow-2xl hover:shadow-primary-100/20 transition-all">
                <div className="p-5 bg-white rounded-[2rem] shadow-sm text-primary-600 w-fit mb-8 group-hover:scale-110 transition-transform">
                  {item.icon}
                </div>
                <h3 className="text-2xl font-black text-gray-900 mb-4">{item.title}</h3>
                <p className="text-gray-400 font-medium leading-relaxed">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials (The Social Soul) */}
      <section className="py-32 px-8">
        <div className="max-w-7xl mx-auto">
          <div className="bg-gray-900 rounded-[4rem] p-12 md:p-24 relative overflow-hidden">
            <div className="absolute top-0 right-0 p-12 opacity-10">
              <Sparkles size={200} className="text-white" />
            </div>

            <div className="relative z-10 max-w-4xl">
              <div className="flex gap-2 mb-8">
                {[1, 2, 3, 4, 5].map(i => <Star key={i} size={24} className="text-primary-400 fill-primary-400" />)}
              </div>
              <h2 className="text-3xl md:text-5xl font-black text-white leading-tight mb-12 italic">
                "The 1:1 interaction model on Skileez completely transformed my approach to learning. It's not just a course; it's a mentorship journey."
              </h2>
              <div className="flex items-center gap-6">
                <div className="w-16 h-16 bg-gradient-to-tr from-primary-400 to-purple-500 rounded-2xl shadow-lg"></div>
                <div>
                  <p className="text-xl font-black text-white">Alexander Chen</p>
                  <p className="text-primary-400 font-bold uppercase tracking-widest text-xs">Senior Product Lead @ V1 Scale</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-32 px-8 text-center bg-gray-50">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-5xl font-black text-gray-900 mb-8 tracking-tighter italic underline decoration-primary-500 decoration-8 underline-offset-8">Ready to evolve?</h2>
          <p className="text-xl text-gray-400 font-medium mb-12">Join thousands of learners and experts today. The session starts now.</p>
          <Link href="/auth/signup" className="inline-block py-6 px-16 bg-gray-900 text-white font-black rounded-[2.5rem] shadow-2xl hover:bg-gray-800 hover:-translate-y-1 transition-all text-xl">
            Start Your Journey
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-20 px-8 border-t border-gray-100">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-12 text-center md:text-left">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center shadow-lg">
              <Zap className="text-white fill-white" size={16} />
            </div>
            <span className="text-xl font-black tracking-tighter">SKILEEZ.</span>
          </div>

          <p className="text-gray-400 text-sm font-medium">
            © 2026 Skileez Platform. Engineered for the 1:1 Mastery. <br className="md:hidden" />
            <span className="text-gray-300 ml-2">All rights reserved.</span>
          </p>

          <div className="flex gap-8 text-[10px] font-black uppercase tracking-widest text-gray-400">
            <a href="#" className="hover:text-primary-600 transition-colors">Privacy</a>
            <a href="#" className="hover:text-primary-600 transition-colors">Terms</a>
            <a href="#" className="hover:text-primary-600 transition-colors">Contact</a>
          </div>
        </div>
      </footer>
    </div>
  );
}
