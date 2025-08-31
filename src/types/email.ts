export interface Email {
  id: string;
  from: string;
  to: string;
  subject: string;
  body: string;
  timestamp: Date;
  isRead: boolean;
  priority: 'high' | 'medium' | 'low';
  category: 'work' | 'personal' | 'promotional' | 'social';
  hasAttachment: boolean;
  summary?: string;
  sentiment: 'positive' | 'neutral' | 'negative';
  urgency: number; // 1-10 scale
}

export interface EmailSummary {
  id: string;
  emailId: string;
  summary: string;
  keyPoints: string[];
  actionItems: string[];
  sentiment: 'positive' | 'neutral' | 'negative';
  urgency: number;
  suggestedResponse?: string;
}

export interface Reminder {
  id: string;
  title: string;
  description: string;
  dueDate: Date;
  priority: 'high' | 'medium' | 'low';
  completed: boolean;
  emailId?: string;
  type: 'task' | 'meeting' | 'followup' | 'deadline';
}

export interface CalendarEvent {
  id: string;
  title: string;
  description: string;
  startTime: Date;
  endTime: Date;
  attendees: string[];
  location?: string;
  type: 'meeting' | 'call' | 'event' | 'reminder';
}