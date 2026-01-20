import Link from "next/link";
import { Mail, Github, Twitter, Instagram } from "lucide-react";

export function Footer() {
    return (
        <footer className="bg-foreground text-background">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-12">
                    {/* Brand */}
                    <div className="col-span-1 md:col-span-1">
                        <Link href="/" className="flex items-center space-x-3 mb-6 group">
                            <div className="w-10 h-10 bg-gradient-to-br from-primary to-secondary rounded-xl flex items-center justify-center shadow-lg">
                                <span className="text-white font-bold text-xl">S</span>
                            </div>
                            <span className="text-2xl font-black tracking-tight">Skileez</span>
                        </Link>
                        <p className="text-muted-foreground leading-relaxed text-sm">
                            The global marketplace for learning and teaching any skill with expert coaches worldwide.
                        </p>
                    </div>

                    {/* Links: For Students */}
                    <div>
                        <h3 className="font-bold mb-6 text-sm uppercase tracking-widest text-primary">For Students</h3>
                        <ul className="space-y-4 text-sm font-medium text-muted-foreground">
                            <li><Link href="/marketplace" className="hover:text-white transition-colors">Find Coaches</Link></li>
                            <li><Link href="/requests/new" className="hover:text-white transition-colors">Post Requests</Link></li>
                            <li><Link href="/marketplace?tab=skills" className="hover:text-white transition-colors">Browse Skills</Link></li>
                        </ul>
                    </div>

                    {/* Links: For Coaches */}
                    <div>
                        <h3 className="font-bold mb-6 text-sm uppercase tracking-widest text-secondary">For Coaches</h3>
                        <ul className="space-y-4 text-sm font-medium text-muted-foreground">
                            <li><Link href="/marketplace" className="hover:text-white transition-colors">Find Work</Link></li>
                            <li><Link href="/profile/edit" className="hover:text-white transition-colors">Create Profile</Link></li>
                            <li><Link href="/stories" className="hover:text-white transition-colors">Success Stories</Link></li>
                        </ul>
                    </div>

                    {/* Links: Company */}
                    <div>
                        <h3 className="font-bold mb-6 text-sm uppercase tracking-widest text-muted-foreground">Company</h3>
                        <ul className="space-y-4 text-sm font-medium text-muted-foreground">
                            <li><Link href="/about" className="hover:text-white transition-colors">About Skileez</Link></li>
                            <li><Link href="/support" className="hover:text-white transition-colors">Support Center</Link></li>
                            <li><Link href="/privacy" className="hover:text-white transition-colors">Privacy Policy</Link></li>
                        </ul>
                    </div>
                </div>

                <div className="mt-20 pt-8 border-t border-white/5 flex flex-col md:flex-row items-center justify-between gap-6">
                    <p className="text-xs text-muted-foreground">
                        &copy; {new Date().getFullYear()} Skileez. All rights reserved. Built with ❤️ for learners and coaches.
                    </p>
                    <div className="flex items-center space-x-6">
                        <Link href="#" className="text-muted-foreground hover:text-white transition-colors"><Twitter className="w-5 h-5" /></Link>
                        <Link href="#" className="text-muted-foreground hover:text-white transition-colors"><Instagram className="w-5 h-5" /></Link>
                        <Link href="#" className="text-muted-foreground hover:text-white transition-colors"><Github className="w-5 h-5" /></Link>
                        <Link href="mailto:contact@skileez.com" className="text-muted-foreground hover:text-white transition-colors"><Mail className="w-5 h-5" /></Link>
                    </div>
                </div>
            </div>
        </footer>
    );
}
