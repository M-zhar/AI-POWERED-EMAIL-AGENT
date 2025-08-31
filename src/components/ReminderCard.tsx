import React from 'react';
import { Reminder } from '../types/email';
import { Clock, CheckCircle, AlertTriangle, Calendar, User, FileText } from 'lucide-react';

interface ReminderCardProps {
  reminder: Reminder;
  onComplete: (id: string) => void;
}

const ReminderCard: React.FC<ReminderCardProps> = ({ reminder, onComplete }) => {
  const formatDueDate = (date: Date) => {
    const now = new Date();
    const diff = date.getTime() - now.getTime();
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    const hours = Math.floor(diff / (1000 * 60 * 60));

    if (diff < 0) return 'Overdue';
    if (days === 0) {
      if (hours <= 1) return 'Due in 1 hour';
      if (hours < 24) return `Due in ${hours} hours`;
    }
    if (days === 1) return 'Due tomorrow';
    if (days < 7) return `Due in ${days} days`;
    return date.toLocaleDateString();
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'border-red-200 bg-red-50';
      case 'medium': return 'border-yellow-200 bg-yellow-50';
      case 'low': return 'border-green-200 bg-green-50';
      default: return 'border-gray-200 bg-white';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'meeting': return <Calendar className="w-4 h-4" />;
      case 'task': return <CheckCircle className="w-4 h-4" />;
      case 'followup': return <User className="w-4 h-4" />;
      case 'deadline': return <FileText className="w-4 h-4" />;
      default: return <Clock className="w-4 h-4" />;
    }
  };

  const isOverdue = new Date() > reminder.dueDate;
  const isUrgent = reminder.dueDate.getTime() - new Date().getTime() < 24 * 60 * 60 * 1000; // less than 24 hours

  return (
    <div className={`rounded-lg border-2 p-4 transition-all duration-200 hover:shadow-md ${
      reminder.completed 
        ? 'border-green-200 bg-green-50 opacity-75'
        : getPriorityColor(reminder.priority)
    }`}>
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-start space-x-3">
          <div className={`p-2 rounded-lg ${
            reminder.completed ? 'bg-green-200 text-green-700' :
            reminder.priority === 'high' ? 'bg-red-100 text-red-600' :
            reminder.priority === 'medium' ? 'bg-yellow-100 text-yellow-600' :
            'bg-blue-100 text-blue-600'
          }`}>
            {getTypeIcon(reminder.type)}
          </div>
          <div className="flex-1">
            <h3 className={`font-semibold text-gray-900 mb-1 ${
              reminder.completed ? 'line-through text-gray-600' : ''
            }`}>
              {reminder.title}
            </h3>
            <p className="text-sm text-gray-600 mb-2">{reminder.description}</p>
            <div className="flex items-center space-x-4 text-xs text-gray-500">
              <div className="flex items-center space-x-1">
                <Clock className="w-3 h-3" />
                <span className={`${isOverdue ? 'text-red-600 font-medium' : isUrgent ? 'text-orange-600' : ''}`}>
                  {formatDueDate(reminder.dueDate)}
                </span>
              </div>
              <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                reminder.type === 'meeting' ? 'bg-blue-100 text-blue-700' :
                reminder.type === 'task' ? 'bg-green-100 text-green-700' :
                reminder.type === 'followup' ? 'bg-purple-100 text-purple-700' :
                'bg-gray-100 text-gray-700'
              }`}>
                {reminder.type}
              </span>
            </div>
          </div>
        </div>
        
        {(isOverdue || isUrgent) && !reminder.completed && (
          <AlertTriangle className={`w-5 h-5 ${isOverdue ? 'text-red-500' : 'text-orange-500'}`} />
        )}
      </div>

      {!reminder.completed && (
        <button
          onClick={() => onComplete(reminder.id)}
          className="w-full mt-3 px-4 py-2 bg-white border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors flex items-center justify-center space-x-2"
        >
          <CheckCircle className="w-4 h-4" />
          <span>Mark as Complete</span>
        </button>
      )}
    </div>
  );
};

export default ReminderCard;