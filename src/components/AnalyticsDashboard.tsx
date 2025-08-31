import React from 'react';
import { Email, Reminder } from '../types/email';
import { BarChart3, TrendingUp, Mail, Clock, CheckCircle, AlertTriangle } from 'lucide-react';

interface AnalyticsDashboardProps {
  emails: Email[];
  reminders: Reminder[];
}

const AnalyticsDashboard: React.FC<AnalyticsDashboardProps> = ({ emails, reminders }) => {
  // Calculate metrics
  const totalEmails = emails.length;
  const unreadEmails = emails.filter(email => !email.isRead).length;
  const highPriorityEmails = emails.filter(email => email.priority === 'high').length;
  const totalReminders = reminders.length;
  const completedReminders = reminders.filter(r => r.completed).length;
  const overdueReminders = reminders.filter(r => !r.completed && new Date() > r.dueDate).length;

  // Email categories distribution
  const categoryStats = {
    work: emails.filter(e => e.category === 'work').length,
    personal: emails.filter(e => e.category === 'personal').length,
    promotional: emails.filter(e => e.category === 'promotional').length,
    social: emails.filter(e => e.category === 'social').length,
  };

  // Sentiment analysis
  const sentimentStats = {
    positive: emails.filter(e => e.sentiment === 'positive').length,
    neutral: emails.filter(e => e.sentiment === 'neutral').length,
    negative: emails.filter(e => e.sentiment === 'negative').length,
  };

  const StatCard: React.FC<{ title: string; value: string | number; subtitle: string; icon: React.ReactNode; color: string }> = 
    ({ title, value, subtitle, icon, color }) => (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-gray-600">{title}</p>
            <p className={`text-2xl font-bold ${color} mt-1`}>{value}</p>
            <p className="text-xs text-gray-500 mt-1">{subtitle}</p>
          </div>
          <div className={`p-3 rounded-full ${color.includes('red') ? 'bg-red-100' : 
            color.includes('blue') ? 'bg-blue-100' : 
            color.includes('green') ? 'bg-green-100' : 
            'bg-yellow-100'}`}>
            {icon}
          </div>
        </div>
      </div>
    );

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900 flex items-center">
          <BarChart3 className="w-7 h-7 mr-3 text-blue-600" />
          Analytics Dashboard
        </h2>
        <div className="text-sm text-gray-500">
          Last updated: {new Date().toLocaleString()}
        </div>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Total Emails"
          value={totalEmails}
          subtitle={`${unreadEmails} unread`}
          icon={<Mail className="w-6 h-6 text-blue-600" />}
          color="text-blue-600"
        />
        <StatCard
          title="High Priority"
          value={highPriorityEmails}
          subtitle="Urgent emails"
          icon={<AlertTriangle className="w-6 h-6 text-red-600" />}
          color="text-red-600"
        />
        <StatCard
          title="Reminders"
          value={`${completedReminders}/${totalReminders}`}
          subtitle="Completed"
          icon={<CheckCircle className="w-6 h-6 text-green-600" />}
          color="text-green-600"
        />
        <StatCard
          title="Overdue"
          value={overdueReminders}
          subtitle="Tasks behind schedule"
          icon={<Clock className="w-6 h-6 text-orange-600" />}
          color="text-orange-600"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Email Categories */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Email Categories</h3>
          <div className="space-y-3">
            {Object.entries(categoryStats).map(([category, count]) => (
              <div key={category} className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className={`w-3 h-3 rounded-full ${
                    category === 'work' ? 'bg-blue-500' :
                    category === 'personal' ? 'bg-purple-500' :
                    category === 'promotional' ? 'bg-orange-500' :
                    'bg-pink-500'
                  }`}></div>
                  <span className="text-sm font-medium text-gray-700 capitalize">{category}</span>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="text-sm text-gray-600">{count}</span>
                  <div className="w-16 bg-gray-200 rounded-full h-2">
                    <div 
                      className={`h-2 rounded-full ${
                        category === 'work' ? 'bg-blue-500' :
                        category === 'personal' ? 'bg-purple-500' :
                        category === 'promotional' ? 'bg-orange-500' :
                        'bg-pink-500'
                      }`}
                      style={{ width: `${(count / totalEmails) * 100}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Sentiment Analysis */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Sentiment Analysis</h3>
          <div className="space-y-3">
            {Object.entries(sentimentStats).map(([sentiment, count]) => (
              <div key={sentiment} className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className={`p-1 rounded-full ${
                    sentiment === 'positive' ? 'bg-green-100' :
                    sentiment === 'neutral' ? 'bg-gray-100' :
                    'bg-red-100'
                  }`}>
                    <TrendingUp className={`w-4 h-4 ${
                      sentiment === 'positive' ? 'text-green-600' :
                      sentiment === 'neutral' ? 'text-gray-600' :
                      'text-red-600'
                    }`} />
                  </div>
                  <span className="text-sm font-medium text-gray-700 capitalize">{sentiment}</span>
                </div>
                <div className="flex items-center space-x-2">
                  <span className="text-sm text-gray-600">{count}</span>
                  <div className="w-16 bg-gray-200 rounded-full h-2">
                    <div 
                      className={`h-2 rounded-full ${
                        sentiment === 'positive' ? 'bg-green-500' :
                        sentiment === 'neutral' ? 'bg-gray-500' :
                        'bg-red-500'
                      }`}
                      style={{ width: `${(count / totalEmails) * 100}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Weekly Overview */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Weekly Productivity Overview</h3>
        <div className="grid grid-cols-7 gap-2">
          {['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'].map((day, index) => (
            <div key={day} className="text-center">
              <div className="text-xs text-gray-600 mb-2">{day}</div>
              <div className={`h-16 rounded-lg flex items-end justify-center ${
                index < 5 ? 'bg-blue-100' : 'bg-gray-100'
              }`}>
                <div 
                  className={`w-full rounded-lg ${
                    index < 5 ? 'bg-blue-500' : 'bg-gray-400'
                  }`}
                  style={{ height: `${Math.random() * 60 + 20}%` }}
                ></div>
              </div>
              <div className="text-xs text-gray-500 mt-1">
                {Math.floor(Math.random() * 20 + 5)}
              </div>
            </div>
          ))}
        </div>
        <p className="text-sm text-gray-600 mt-4 text-center">
          Average daily email processing efficiency
        </p>
      </div>
    </div>
  );
};

export default AnalyticsDashboard;