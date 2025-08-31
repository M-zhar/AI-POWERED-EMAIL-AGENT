import React, { useState } from 'react';
import { useEmails } from './hooks/useEmails';
import Sidebar from './components/Sidebar';
import EmailCard from './components/EmailCard';
import EmailDetails from './components/EmailDetails';
import ReminderCard from './components/ReminderCard';
import CalendarView from './components/CalendarView';
import AnalyticsDashboard from './components/AnalyticsDashboard';
import LoadingSpinner from './components/LoadingSpinner';
import { Search, Filter, RefreshCw, Zap } from 'lucide-react';

type ActiveTab = 'emails' | 'calendar' | 'reminders' | 'analytics';

function App() {
  const { emails, summaries, reminders, calendarEvents, loading, markAsRead, generateSummary, completeReminder } = useEmails();
  const [activeTab, setActiveTab] = useState<ActiveTab>('emails');
  const [selectedEmail, setSelectedEmail] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterPriority, setFilterPriority] = useState<'all' | 'high' | 'medium' | 'low'>('all');
  const [generatingSummary, setGeneratingSummary] = useState<string | null>(null);

  const unreadCount = emails.filter(email => !email.isRead).length;
  const pendingReminders = reminders.filter(reminder => !reminder.completed).length;

  const filteredEmails = emails.filter(email => {
    const matchesSearch = email.subject.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         email.from.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         email.body.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesPriority = filterPriority === 'all' || email.priority === filterPriority;
    return matchesSearch && matchesPriority;
  });

  const handleSummarize = async (emailId: string) => {
    setGeneratingSummary(emailId);
    await generateSummary(emailId);
    setGeneratingSummary(null);
  };

  const handleEmailClick = (emailId: string) => {
    setSelectedEmail(emailId);
    markAsRead(emailId);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <LoadingSpinner />
          <p className="text-gray-600 mt-4">Loading your email agent...</p>
        </div>
      </div>
    );
  }

  if (selectedEmail) {
    const email = emails.find(e => e.id === selectedEmail);
    const summary = summaries.find(s => s.emailId === selectedEmail);
    
    if (!email) return null;

    return (
      <div className="min-h-screen bg-gray-50">
        <EmailDetails
          email={email}
          summary={summary}
          onBack={() => setSelectedEmail(null)}
          onSummarize={() => handleSummarize(selectedEmail)}
        />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 flex">
      <Sidebar
        activeTab={activeTab}
        onTabChange={setActiveTab}
        unreadCount={unreadCount}
        reminderCount={pendingReminders}
      />
      
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <header className="bg-white border-b border-gray-200 px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <h2 className="text-2xl font-bold text-gray-900 capitalize">{activeTab}</h2>
              {activeTab === 'emails' && (
                <div className="flex items-center space-x-2">
                  <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium">
                    {filteredEmails.length} emails
                  </span>
                  {unreadCount > 0 && (
                    <span className="px-3 py-1 bg-red-100 text-red-800 rounded-full text-sm font-medium">
                      {unreadCount} unread
                    </span>
                  )}
                </div>
              )}
            </div>
            
            <div className="flex items-center space-x-4">
              <button className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors">
                <RefreshCw className="w-5 h-5" />
              </button>
              <button className="flex items-center px-4 py-2 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-lg hover:from-blue-700 hover:to-indigo-700 transition-all">
                <Zap className="w-4 h-4 mr-2" />
                AI Insights
              </button>
            </div>
          </div>

          {activeTab === 'emails' && (
            <div className="flex items-center space-x-4 mt-4">
              <div className="flex-1 relative">
                <Search className="w-5 h-5 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search emails..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
              <div className="flex items-center space-x-2">
                <Filter className="w-5 h-5 text-gray-400" />
                <select
                  value={filterPriority}
                  onChange={(e) => setFilterPriority(e.target.value as any)}
                  className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="all">All Priorities</option>
                  <option value="high">High Priority</option>
                  <option value="medium">Medium Priority</option>
                  <option value="low">Low Priority</option>
                </select>
              </div>
            </div>
          )}
        </header>

        {/* Content */}
        <main className="flex-1 overflow-auto p-6">
          {activeTab === 'emails' && (
            <div className="max-w-4xl mx-auto">
              <div className="space-y-4">
                {filteredEmails.length === 0 ? (
                  <div className="text-center py-12">
                    <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                      <Search className="w-8 h-8 text-gray-400" />
                    </div>
                    <p className="text-gray-600">No emails found</p>
                    <p className="text-sm text-gray-500 mt-1">Try adjusting your search or filter criteria</p>
                  </div>
                ) : (
                  filteredEmails.map((email) => (
                    <EmailCard
                      key={email.id}
                      email={email}
                      summary={summaries.find(s => s.emailId === email.id)}
                      onClick={() => handleEmailClick(email.id)}
                      onSummarize={() => handleSummarize(email.id)}
                    />
                  ))
                )}
              </div>
            </div>
          )}

          {activeTab === 'reminders' && (
            <div className="max-w-4xl mx-auto">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {reminders.length === 0 ? (
                  <div className="col-span-full text-center py-12">
                    <p className="text-gray-600">No reminders yet</p>
                    <p className="text-sm text-gray-500 mt-1">Your AI assistant will create reminders from your emails</p>
                  </div>
                ) : (
                  reminders.map((reminder) => (
                    <ReminderCard
                      key={reminder.id}
                      reminder={reminder}
                      onComplete={completeReminder}
                    />
                  ))
                )}
              </div>
            </div>
          )}

          {activeTab === 'calendar' && (
            <div className="max-w-4xl mx-auto">
              <CalendarView events={calendarEvents} />
            </div>
          )}

          {activeTab === 'analytics' && (
            <div className="max-w-6xl mx-auto">
              <AnalyticsDashboard emails={emails} reminders={reminders} />
            </div>
          )}
        </main>
      </div>

      {/* Loading overlay for summary generation */}
      {generatingSummary && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 text-center">
            <LoadingSpinner />
            <p className="text-gray-600 mt-4">Generating AI summary...</p>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;