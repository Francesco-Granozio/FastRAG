import { Link, useLocation } from 'react-router-dom';
import { FileText, Database } from 'lucide-react';
import type { NavItem } from '../../types';

const Navbar = () => {
  const location = useLocation();

  const navItems: NavItem[] = [
    { path: '/', label: 'Upload & Query', icon: FileText },
    { path: '/files', label: 'Embedded Files', icon: Database },
  ];

  return (
    <nav className="fixed left-0 top-0 h-full w-64 bg-slate-800 border-r border-slate-700">
      <div className="flex flex-col h-full">
        <div className="flex-shrink-0 px-6 py-6 border-b border-slate-700">
          <h1 className="text-xl font-bold text-slate-100">
            RAG Application
          </h1>
        </div>
        <div className="flex-1 px-4 py-4 space-y-2">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center px-4 py-3 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-blue-600 text-white'
                    : 'text-slate-300 hover:bg-slate-700 hover:text-slate-100'
                }`}
              >
                <Icon className="w-5 h-5 mr-3" />
                {item.label}
              </Link>
            );
          })}
        </div>
      </div>
    </nav>
  );
};

export default Navbar;

