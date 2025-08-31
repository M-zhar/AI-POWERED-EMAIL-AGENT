import React from 'react';
import { Mail, Calendar, Bell, BarChart3, Settings, Bot } from 'lucide-react';

interface SidebarProps {
  activeTab: 'emails' | 'calendar' | 'reminders' | 'analytics';
  onTabChange: (tab: 'emails' | 'calendar' | 'reminders' | 'analytics') => void;
  unreadCount: number;
  reminderCount: number;
}

const Sidebar: React.FC<SidebarProps> = ({ activeTab, onTabChange, unreadCount, reminderCount }) => {
  const menuItems = [
    { id: 'emails', label: 'Emails', icon: Mail, count: unreadCount },
    { id: 'calendar', label: 'Calendar', icon: Calendar, count: 0 },
    { id: 'reminders', label: 'Reminders', icon: Bell, count: reminderCount },
    { id: 'analytics', label: 'Analytics', icon: BarChart3, count: 0 }
  ] as const;

  return (
    <div className="w-64 bg-white border-r border-gray-200 flex flex-col h-full">
      {/* Header */}
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-indigo-700 rounded-xl flex items-center justify-center">
            <Bot className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-gray-900">EmailAgent</h1>
            <p className="text-sm text-gray-600">AI-Powered Assistant</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4">
        <ul className="space-y-2">
          {menuItems.map((item) => (
            <li key={item.id}>
              <button
                onClick={() => onTabChange(item.id)}
                className={`w-full flex items-center justify-between p-3 rounded-lg transition-all duration-200 ${
                  activeTab === item.id
                    ? 'bg-blue-100 text-blue-700 shadow-sm'
                    : 'text-gray-700 hover:bg-gray-100'
                }`}
              >
                <div className="flex items-center space-x-3">
                  <item.icon className="w-5 h-5" />
                  <span className="font-medium">{item.label}</span>
                </div>
                {item.count > 0 && (
                  <span className="bg-red-500 text-white text-xs font-medium px-2 py-1 rounded-full min-w-[20px] text-center">
                    {item.count}
                  </span>
                )}
              </button>
            </li>
          ))}
        </ul>
      </nav>

      {/* Footer */}
      <div className="p-4 border-t border-gray-200">
        <button className="w-full flex items-center space-x-3 p-3 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors">
          <Settings className="w-5 h-5" />
          <span className="font-medium">Settings</span>
        </button>
      </div>
    </div>
  );
};

export default Sidebar;