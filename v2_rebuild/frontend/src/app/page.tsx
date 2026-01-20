"use client";

import Link from "next/link";
import {
  Zap,
  ArrowRight,
  Star,
  Users,
  ShieldCheck,
  Sparkles,
  Globe,
  Award,
  Play,
  Check,
  Search,
  BookOpen,
  Calendar,
  MessageCircle,
  TrendingUp,
  Camera,
  Music,
  Code,
  DollarSign,
  Edit3
} from "lucide-react";
import { motion, useScroll, useTransform } from "framer-motion";
import { useRef } from "react";

export default function LandingPage() {
  const containerRef = useRef(null);
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ["start start", "end start"],
  });

  const icons = [
    { Icon: Edit3, color: "from-purple-500 to-purple-700", top: "15%", left: "8%", right: undefined, bottom: undefined, speed: 0.3, rotation: 12 },
    { Icon: TrendingUp, color: "from-blue-500 to-blue-700", top: "25%", right: "12%", left: undefined, bottom: undefined, speed: 0.6, rotation: -6 },
    { Icon: DollarSign, color: "from-emerald-500 to-emerald-700", bottom: "28%", left: "15%", top: undefined, right: undefined, speed: 1.2, rotation: 45 },
    { Icon: Code, color: "from-orange-500 to-orange-700", bottom: "48%", right: "8%", top: undefined, left: undefined, speed: 0.4, rotation: -12 },
    { Icon: Music, color: "from-pink-500 to-pink-700", bottom: "36%", right: "20%", top: undefined, left: undefined, speed: 0.8, rotation: 6 },
    { Icon: Camera, color: "from-yellow-400 to-yellow-600", bottom: "72%", left: "4%", top: undefined, right: undefined, speed: 1.5, rotation: 12 },
  ];

  return (
    <div ref={containerRef} className="overflow-x-hidden">
      {/* Hero Section */}
      <section className="relative min-h-[90vh] flex items-center justify-center pt-20">
        {/* Background Decorative Elements (V1 Soul) */}
        <div className="absolute inset-0 overflow-hidden pointer-events-none">
          <div className="absolute top-[-10%] right-[-10%] w-[50%] h-[50%] bg-primary/10 rounded-full blur-[120px]"></div>
          <div className="absolute bottom-[-10%] left-[-10%] w-[40%] h-[40%] bg-secondary/10 rounded-full blur-[100px]"></div>

          {/* Falling Icons (V1 Mirror) */}
          {icons.map((item, i) => (
            <FallingIcon key={i} {...item} scrollYProgress={scrollYProgress} />
          ))}
        </div>

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center relative z-10">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="inline-flex items-center bg-white/60 backdrop-blur-md border border-gray-200/50 rounded-full px-4 py-2 mb-8 shadow-sm"
          >
            <div className="w-2 h-2 bg-success rounded-full mr-2 animate-pulse"></div>
            <span className="text-sm font-bold text-gray-700">Best Learning Platform</span>
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="text-5xl md:text-8xl font-black text-gray-900 leading-[0.9] tracking-tighter mb-8"
          >
            Skileez make sure you<br />
            <span className="text-primary italic">never start from</span><br />
            <span className="text-secondary">scratch</span>
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="text-xl md:text-2xl text-gray-500 font-medium max-w-2xl mx-auto leading-relaxed mb-12"
          >
            Unlock the library of 10K+ expert coaches and mentors. Learn any skill for your next project.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.3 }}
            className="flex flex-col sm:flex-row items-center justify-center gap-6"
          >
            <Link href="/auth/signup?role=coach" className="btn-primary px-10 py-5 text-lg">
              Become a Coach
            </Link>
            <Link href="/auth/signup?role=student" className="px-10 py-5 bg-white border border-gray-200 text-gray-900 font-black rounded-xl text-lg hover:bg-gray-50 hover:shadow-xl transition-all shadow-sm">
              Start Learning
            </Link>
          </motion.div>
        </div>
      </section>

      {/* How It Works (V1 Mirror) */}
      <section className="py-32 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-24">
            <h2 className="text-4xl md:text-6xl font-black text-gray-900 mb-6 tracking-tight">How It Works</h2>
            <p className="text-xl text-gray-400 font-bold uppercase tracking-widest text-sm">Simple steps to start your learning journey</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-12">
            {[
              {
                step: 1,
                title: "Create Profile",
                desc: "Join as a student or coach. Set up your profile in minutes and start connecting.",
                icon: UserIcon,
                color: "bg-primary"
              },
              {
                step: 2,
                title: "Find Your Match",
                desc: "Browse expert coaches or post learning requests. Smart matching finds your perfect fit.",
                icon: Search,
                color: "bg-success"
              },
              {
                step: 3,
                title: "Start Learning",
                desc: "Book sessions, track progress, and achieve your goals with personalized coaching.",
                icon: Zap,
                color: "bg-orange-500"
              }
            ].map((item, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
                className="text-center group"
              >
                <div className="relative mb-8">
                  <div className={`w-24 h-24 ${item.color} rounded-[2rem] flex items-center justify-center mx-auto shadow-xl group-hover:scale-110 transition-transform duration-500`}>
                    <item.icon className="w-10 h-10 text-white" />
                  </div>
                  <div className="absolute -top-2 -right-2 w-10 h-10 bg-secondary text-white rounded-full flex items-center justify-center text-lg font-black shadow-lg">
                    {item.step}
                  </div>
                </div>
                <h3 className="text-2xl font-black text-gray-900 mb-4">{item.title}</h3>
                <p className="text-gray-400 font-medium leading-relaxed">{item.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Why Choose Skileez (V1 Mirror) */}
      <section className="py-32 bg-muted/30">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-20">
            <h2 className="text-4xl md:text-6xl font-black text-gray-900 mb-6 tracking-tight">Why Choose Skileez?</h2>
            <p className="text-xl text-gray-400 font-bold uppercase tracking-widest text-sm">Premium features designed for effective learning</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {[
              { icon: ShieldCheck, title: "Verified Coaches", color: "text-primary", desc: "All coaches go through a thorough verification process to ensure quality." },
              { icon: MessageCircle, title: "Direct Messaging", color: "text-success", desc: "Communicate directly with coaches through our secure messaging platform." },
              { icon: Calendar, title: "Flexible Scheduling", color: "text-secondary", desc: "Book sessions that fit your schedule with easy-to-use tools." },
              { icon: TrendingUp, title: "Progress Tracking", color: "text-orange-500", desc: "Monitor your learning progress with detailed session tracking." },
              { icon: DollarSign, title: "Secure Payments", color: "text-pink-500", desc: "Safe and secure payment processing with milestone-based releases." },
              { icon: Globe, title: "Global Community", color: "text-indigo-500", desc: "Connect with learners and coaches from around the world." },
            ].map((feature, i) => (
              <motion.div
                key={i}
                whileHover={{ y: -8 }}
                className="premium-card"
              >
                <div className={`w-14 h-14 bg-white shadow-md border border-gray-100 rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform`}>
                  <feature.icon className={`w-8 h-8 ${feature.color}`} />
                </div>
                <h3 className="text-xl font-black text-gray-900 mb-4">{feature.title}</h3>
                <p className="text-gray-400 font-medium leading-relaxed">{feature.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Exclusive Community Section (V1 Soul) */}
      <section className="py-32 px-4">
        <div className="max-w-5xl mx-auto">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            className="relative glass-panel rounded-[3rem] p-8 md:p-20 overflow-hidden text-center"
          >
            {/* Background Blob */}
            <div className="absolute -top-24 -right-24 w-64 h-64 bg-primary/10 rounded-full blur-[80px]"></div>
            <div className="absolute -bottom-24 -left-24 w-64 h-64 bg-secondary/10 rounded-full blur-[80px]"></div>

            <div className="relative z-10">
              <div className="inline-flex items-center bg-gradient-to-r from-primary to-secondary text-white px-6 py-2 rounded-full text-xs font-black uppercase tracking-widest mb-8 shadow-xl">
                <Star className="w-4 h-4 mr-2 fill-white" />
                Exclusive Community
              </div>

              <h2 className="text-3xl md:text-5xl font-black text-gray-900 mb-6 leading-tight">
                Join Our <span className="text-primary italic">Exclusive</span> Community
              </h2>

              <p className="text-lg md:text-xl text-gray-500 font-medium mb-10 max-w-3xl mx-auto">
                Connect with top-tier coaches and ambitious learners. Get access to premium content, events, and mentorship.
              </p>

              {/* Limited Spots Alert (V1 Mirror) */}
              <div className="bg-error/5 border border-error/10 rounded-2xl p-6 mb-12 max-w-lg mx-auto">
                <div className="flex items-center justify-center mb-4">
                  <div className="w-3 h-3 bg-error rounded-full animate-pulse mr-3"></div>
                  <span className="text-error font-black uppercase tracking-widest text-sm">Only 500 Spots Available</span>
                </div>
                <div className="text-gray-400 text-sm font-bold mb-4">
                  347 spots taken • 153 remaining
                </div>
                <div className="bg-error/10 h-2 rounded-full overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    whileInView={{ width: "69.4%" }}
                    transition={{ duration: 1.5, ease: "easeOut" }}
                    className="bg-error h-full"
                  />
                </div>
              </div>

              <div className="flex flex-col items-center gap-4">
                <button className="btn-primary px-12 py-5 text-xl flex items-center gap-3">
                  Join Community Now <ArrowRight className="w-6 h-6" />
                </button>
                <p className="text-xs text-gray-400 font-bold uppercase tracking-widest">
                  Free to join • No credit card required
                </p>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Final CTA (V1 Mirror Style) */}
      <section className="py-40 relative overflow-hidden bg-foreground text-white">
        <div className="max-w-7xl mx-auto px-4 text-center relative z-10">
          <h2 className="text-4xl md:text-7xl font-black mb-10 leading-tight">
            Where your <span className="text-primary italic">skills</span> turn<br />
            into <span className="text-secondary italic">success</span> with a click
          </h2>
          <p className="text-xl md:text-2xl text-gray-400 font-medium max-w-3xl mx-auto mb-16">
            Build custom learning paths, connect with expert coaches, and transform your career effortlessly.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-8">
            <button className="bg-white text-gray-900 px-12 py-5 rounded-2xl font-black text-xl hover:bg-gray-100 hover:scale-105 transition-all shadow-2xl flex items-center gap-3">
              <Play className="w-6 h-6 fill-gray-900" />
              Watch Demo
            </button>
            <Link href="/auth/signup" className="text-xl font-bold border-b-2 border-primary hover:text-primary transition-all pb-1">
              Start your journey today
            </Link>
          </div>
        </div>

        {/* Abstract Shapes */}
        <div className="absolute top-0 left-0 w-full h-full opacity-10 pointer-events-none">
          <div className="absolute top-0 right-[-10%] w-[60%] h-[60%] border border-white/20 rounded-full rotate-45"></div>
          <div className="absolute bottom-[-10%] left-[-10%] w-[40%] h-[40%] border border-white/20 rounded-full -rotate-12"></div>
        </div>
      </section>
    </div>
  );
}

interface FallingIconProps {
  Icon: any;
  color: string;
  top?: string;
  bottom?: string;
  left?: string;
  right?: string;
  speed: number;
  rotation: number;
  scrollYProgress: any;
}

function FallingIcon({ Icon, color, top, bottom, left, right, speed, rotation, scrollYProgress }: FallingIconProps) {
  const y = useTransform(scrollYProgress, [0, 1], [0, 500 * speed]);
  const rotate = useTransform(scrollYProgress, [0, 1], [rotation, rotation + 180 * speed]);
  const opacity = useTransform(scrollYProgress, [0, 0.5], [1, 0]);
  const scale = useTransform(scrollYProgress, [0, 0.5], [1, 1.2]);

  return (
    <motion.div
      style={{
        position: "absolute",
        top,
        bottom,
        left,
        right,
        y,
        rotate,
        opacity,
        scale,
        zIndex: 1
      }}
      className="hidden lg:flex"
    >
      <div className={`w-20 h-20 xl:w-24 xl:h-24 bg-gradient-to-br ${color} rounded-3xl flex items-center justify-center shadow-2xl border border-white/10`}>
        <Icon className="w-10 h-10 xl:w-12 xl:h-12 text-white" />
      </div>
    </motion.div>
  );
}

function UserIcon(props: any) {
  return (
    <svg
      {...props}
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" /><circle cx="9" cy="7" r="4" /><line x1="19" y1="8" x2="19" y2="14" /><line x1="22" y1="11" x2="16" y2="11" />
    </svg>
  );
}
