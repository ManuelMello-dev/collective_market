import { Link } from "wouter";
import { useAuth } from "@/_core/hooks/useAuth";
import { getLoginUrl } from "@/const";

export default function DashboardNav() {
  const { user, logout, isAuthenticated } = useAuth();

  const navItems = [
    { label: "MARKET", href: "/market" },
    { label: "PORTFOLIO", href: "/portfolio" },
    { label: "SIMULATION", href: "/simulation" },
    { label: "HEALTH", href: "/health" },
    { label: "HISTORY", href: "/history" },
    { label: "ALERTS", href: "/alerts" },
    { label: "REPLAY", href: "/replay" },
    { label: "POSITION", href: "/position" },
  ];

  return (
    <nav className="fixed left-0 top-0 w-64 h-screen bg-background border-r-4 border-foreground flex flex-col">
      {/* Logo */}
      <div className="p-8 border-b-4 border-foreground">
        <h1 className="text-3xl font-black tracking-tighter">
          MARKET
          <br />
          SYSTEM
        </h1>
        <p className="text-xs font-mono tracking-widest mt-4 text-muted">
          INTELLIGENCE DASHBOARD
        </p>
      </div>

      {/* Navigation */}
      <div className="flex-1 overflow-y-auto p-8 space-y-4">
        {navItems.map((item) => (
          <Link key={item.href} href={item.href}>
            <a className="block px-4 py-3 font-bold text-sm tracking-wider border-2 border-foreground hover:bg-foreground hover:text-background transition-colors">
              {item.label}
            </a>
          </Link>
        ))}
      </div>

      {/* Footer */}
      <div className="p-8 border-t-4 border-foreground">
        {isAuthenticated ? (
          <div className="space-y-4">
            <div className="text-xs">
              <p className="font-bold tracking-widest">USER</p>
              <p className="text-muted mt-1">{user?.name || user?.email}</p>
            </div>
            <button
              onClick={() => logout()}
              className="w-full px-4 py-2 font-bold text-xs tracking-wider border-2 border-foreground hover:bg-foreground hover:text-background transition-colors"
            >
              LOGOUT
            </button>
          </div>
        ) : (
          <a
            href={getLoginUrl()}
            className="block px-4 py-2 font-bold text-xs tracking-wider border-2 border-foreground hover:bg-foreground hover:text-background transition-colors text-center"
          >
            LOGIN
          </a>
        )}
      </div>
    </nav>
  );
}
