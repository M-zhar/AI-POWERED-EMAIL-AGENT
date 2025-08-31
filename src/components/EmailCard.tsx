import React from 'react';
import { Email, EmailSummary } from '../types/email';
import { Clock, Paperclip, User, AlertTriangle, TrendingUp, TrendingDown, Minus } from 'lucide-react';

interface EmailCardProps {
  email: Email;
  summary?: EmailSummary;
  onClick: () => void;
  onSummarize: () => void;
}

const EmailCard: React.FC<EmailCardProps> = ({ email, summary, onClick, onSummarize }) => {
  const formatTime = (date: Date) => {
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const days = Math.floor(hours / 24);

    if (days > 0) return `${days}d ago`;
    if (hours > 0) return `${hours}h ago`;
    return 'Just now';
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'text-red-600 bg-red-50';
      case 'medium': return 'text-yellow-600 bg-yellow-50';
      case 'low': return 'text-green-600 bg-green-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'work': return 'bg-blue-100 text-blue-800';
      case 'personal': return 'bg-purple-100 text-purple-800';
      case 'promotional': return 'bg-orange-100 text-orange-800';
      case 'social': return 'bg-pink-100 text-pink-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getSentimentIcon = (sentiment: string) => {
    switch (sentiment) {
      case 'positive': return <TrendingUp className="w-4 h-4 text-green-500" />;
      case 'negative': return <TrendingDown className="w-4 h-4 text-red-500" />;
      case 'neutral': return <Minus className="w-4 h-4 text-gray-500" />;
      default: return null;
    }
  };

  return (
    <div
      className={`bg-white rounded-lg shadow-sm border border-gray-200 p-4 hover:shadow-md transition-all duration-200 cursor-pointer ${
        !email.isRead ? 'border-l-4 border-l-blue-500' : ''
      }`}
      onClick={onClick}
    >
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center space-x-2">
          <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
            <User className="w-4 h-4 text-white" />
          </div>
          <div>
            <p className="font-medium text-gray-900 text-sm">{email.from}</p>
            <p className="text-xs text-gray-500 flex items-center">
              <Clock className="w-3 h-3 mr-1" />
              {formatTime(email.timestamp)}
            </p>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          {email.urgency >= 7 && <AlertTriangle className="w-4 h-4 text-red-500" />}
          {email.hasAttachment && <Paperclip className="w-4 h-4 text-gray-400" />}
          {getSentimentIcon(email.sentiment)}
        </div>
      </div>

      <div className="mb-3">
        <h3 className={`font-semibold text-gray-900 mb-1 ${!email.isRead ? 'font-bold' : ''}`}>
          {email.subject}
        </h3>
        <p className="text-gray-600 text-sm line-clamp-2">
          {summary?.summary || email.body.slice(0, 120) + '...'}
        </p>
      </div>

      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <span className={`px-2 py-1 rounded-full text-xs font-medium ${getPriorityColor(email.priority)}`}>
            {email.priority.toUpperCase()}
          </span>
          <span className={`px-2 py-1 rounded-full text-xs font-medium ${getCategoryColor(email.category)}`}>
            {email.category}
          </span>
          <div className="flex items-center text-xs text-gray-500">
            <div className="w-2 h-2 bg-yellow-400 rounded-full mr-1"></div>
            Urgency: {email.urgency}/10
          </div>
        </div>
        
        {!summary && (
          <button
            onClick={(e) => {
              e.stopPropagation();
              onSummarize();
            }}
            className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-xs font-medium hover:bg-blue-200 transition-colors"
          >
            Summarize
          </button>
        )}
      </div>

      {summary && (
        <div className="mt-3 p-3 bg-blue-50 rounded-lg border-l-2 border-blue-300">
          <h4 className="font-medium text-blue-900 mb-2">AI Summary</h4>
          {summary.keyPoints.length > 0 && (
            <div className="mb-2">
              <p className="text-xs font-medium text-blue-800 mb-1">Key Points:</p>
              <ul className="text-xs text-blue-700 space-y-1">
                {summary.keyPoints.slice(0, 2).map((point, index) => (
                  <li key={index} className="flex items-start">
                    <span className="w-1 h-1 bg-blue-400 rounded-full mt-2 mr-2 flex-shrink-0"></span>
                    {point}
                  </li>
                ))}
              </ul>
            </div>
          )}
          {summary.suggestedResponse && (
            <div className="mt-2">
              <p className="text-xs font-medium text-blue-800 mb-1">Suggested Reply:</p>
              <p className="text-xs text-blue-700 italic">{summary.suggestedResponse.slice(0, 80)}...</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default EmailCard;