import { useState, useEffect } from 'react';
import { Email, EmailSummary, Reminder, CalendarEvent } from '../types/email';

const API_BASE_URL = 'http://localhost:8000/api/v1';

export const useEmails = () => {
  const [emails, setEmails] = useState<Email[]>([]);
  const [summaries, setSummaries] = useState<EmailSummary[]>([]);
  const [reminders, setReminders] = useState<Reminder[]>([]);
  const [calendarEvents, setCalendarEvents] = useState<CalendarEvent[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      
      // Fetch emails
      const emailsResponse = await fetch(`${API_BASE_URL}/emails`);
      if (emailsResponse.ok) {
        const emailsData = await emailsResponse.json();
        setEmails(emailsData);
      }
      
      // Fetch reminders
      const remindersResponse = await fetch(`${API_BASE_URL}/reminders`);
      if (remindersResponse.ok) {
        const remindersData = await remindersResponse.json();
        setReminders(remindersData);
      }
      
      // Fetch calendar events
      const eventsResponse = await fetch(`${API_BASE_URL}/events`);
      if (eventsResponse.ok) {
        const eventsData = await eventsResponse.json();
        setCalendarEvents(eventsData);
      }
      
    } catch (error) {
      console.error('Failed to fetch data:', error);
      // Fallback to mock data if API is not available
      const { mockEmails, mockSummaries, mockReminders, mockCalendarEvents } = await import('../data/mockData');
      setEmails(mockEmails);
      setSummaries(mockSummaries);
      setReminders(mockReminders);
      setCalendarEvents(mockCalendarEvents);
    } finally {
      setLoading(false);
    }
  };

  const markAsRead = (emailId: string) => {
    // Update local state
    setEmails(emails.map(email => 
      email.id === emailId ? { ...email, isRead: true } : email
    ));
    
    // Update on server
    fetch(`${API_BASE_URL}/emails/${emailId}/mark-read`, {
      method: 'POST'
    }).catch(error => console.error('Failed to mark email as read:', error));
  };

  const generateSummary = async (emailId: string): Promise<EmailSummary | null> => {
    try {
      // Start summary generation
      const response = await fetch(`${API_BASE_URL}/summaries/${emailId}/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          model: 'openai',
          include_response: true,
          response_tone: 'professional'
        })
      });
      
      if (!response.ok) {
        throw new Error('Failed to generate summary');
      }
      
      // Poll for completion (in a real app, you might use WebSockets)
      let attempts = 0;
      const maxAttempts = 30; // 30 seconds timeout
      
      while (attempts < maxAttempts) {
        await new Promise(resolve => setTimeout(resolve, 1000)); // Wait 1 second
        
        const statusResponse = await fetch(`${API_BASE_URL}/summaries/${emailId}/status`);
        if (statusResponse.ok) {
          const statusData = await statusResponse.json();
          
          if (statusData.exists) {
            // Fetch the complete summary
            const summaryResponse = await fetch(`${API_BASE_URL}/summaries/${emailId}`);
            if (summaryResponse.ok) {
              const summaryData = await summaryResponse.json();
              
              // Convert to our format
              const summary: EmailSummary = {
                id: summaryData.id.toString(),
                emailId,
                summary: summaryData.summary,
                keyPoints: summaryData.key_points || [],
                actionItems: summaryData.action_items || [],
                sentiment: summaryData.sentiment_score > 0.1 ? 'positive' : 
                          summaryData.sentiment_score < -0.1 ? 'negative' : 'neutral',
                urgency: summaryData.urgency_score,
                suggestedResponse: summaryData.suggested_response
              };
              
              setSummaries([...summaries, summary]);
              return summary;
            }
          }
        }
        
        attempts++;
      }
      
      throw new Error('Summary generation timeout');
      
    } catch (error) {
      console.error('Failed to generate summary:', error);
      
      // Fallback to mock summary
      const email = emails.find(e => e.id === emailId);
      if (email) {
        const fallbackSummary: EmailSummary = {
          id: Math.random().toString(),
          emailId,
          summary: `Summary unavailable. Email from ${email.from} about: ${email.subject}`,
          keyPoints: ['AI service temporarily unavailable'],
          actionItems: ['Review email manually'],
          sentiment: email.sentiment,
          urgency: email.urgency,
          suggestedResponse: 'Thank you for your email. I will review this and get back to you soon.'
        };
        
        setSummaries([...summaries, fallbackSummary]);
        return fallbackSummary;
      }
      
      return null;
    }
  };

  const completeReminder = (reminderId: string) => {
    // Update local state
    setReminders(reminders.map(reminder =>
      reminder.id === reminderId ? { ...reminder, completed: true } : reminder
    ));
    
    // Update on server
    fetch(`${API_BASE_URL}/reminders/${reminderId}/complete`, {
      method: 'POST'
    }).catch(error => console.error('Failed to complete reminder:', error));
  };

  return {
    emails,
    summaries,
    reminders,
    calendarEvents,
    loading,
    markAsRead,
    generateSummary,
    completeReminder
  };
};