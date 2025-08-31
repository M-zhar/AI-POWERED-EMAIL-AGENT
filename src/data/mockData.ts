import { Email, EmailSummary, Reminder, CalendarEvent } from '../types/email';

export const mockEmails: Email[] = [
  {
    id: '1',
    from: 'sarah.johnson@techcorp.com',
    to: 'you@company.com',
    subject: 'Q4 Budget Review - Action Required',
    body: `Hi there,

I hope this email finds you well. I need to discuss the Q4 budget allocations with you urgently. We have several line items that require immediate attention:

1. Marketing budget increase of 15%
2. New hiring budget for the engineering team
3. Infrastructure costs for the new data center

Can we schedule a meeting this week to go over these details? The board meeting is next Friday, so we need to finalize everything by Wednesday.

Please let me know your availability.

Best regards,
Sarah Johnson
Finance Director`,
    timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000), // 2 hours ago
    isRead: false,
    priority: 'high',
    category: 'work',
    hasAttachment: true,
    sentiment: 'neutral',
    urgency: 8,
  },
  {
    id: '2',
    from: 'newsletter@designweekly.com',
    to: 'you@company.com',
    subject: '🎨 Design Weekly: Latest UI/UX Trends',
    body: `This week's top design trends and inspiration...

Featured articles:
- The rise of neumorphism in mobile apps
- Color psychology in e-commerce design
- 10 best typography pairings for 2024

Check out our latest resources and free design assets.`,
    timestamp: new Date(Date.now() - 5 * 60 * 60 * 1000), // 5 hours ago
    isRead: true,
    priority: 'low',
    category: 'promotional',
    hasAttachment: false,
    sentiment: 'positive',
    urgency: 2,
  },
  {
    id: '3',
    from: 'mike.chen@clientcompany.com',
    to: 'you@company.com',
    subject: 'Project Milestone Concerns',
    body: `Hello,

I wanted to reach out regarding the current project timeline. We're approaching the second milestone deadline, and I have some concerns about the deliverables.

The testing phase has revealed several issues that might push back our launch date. I think we should discuss these challenges and possibly adjust our timeline.

Could we arrange a call tomorrow morning to address these issues?

Thanks,
Mike Chen`,
    timestamp: new Date(Date.now() - 1 * 24 * 60 * 60 * 1000), // 1 day ago
    isRead: false,
    priority: 'high',
    category: 'work',
    hasAttachment: false,
    sentiment: 'negative',
    urgency: 7,
  },
  {
    id: '4',
    from: 'team@productivity.app',
    to: 'you@company.com',
    subject: 'Your Weekly Productivity Report',
    body: `Great work this week! Here's your productivity summary:

- 27 tasks completed
- 4.2 hours average focus time per day
- 89% email response rate
- 3 meetings attended

Keep up the excellent work! Your productivity has increased by 12% compared to last week.`,
    timestamp: new Date(Date.now() - 12 * 60 * 60 * 1000), // 12 hours ago
    isRead: true,
    priority: 'medium',
    category: 'personal',
    hasAttachment: false,
    sentiment: 'positive',
    urgency: 3,
  }
];

export const mockSummaries: EmailSummary[] = [
  {
    id: '1',
    emailId: '1',
    summary: 'Sarah Johnson from Finance needs urgent discussion about Q4 budget allocations before board meeting next Friday.',
    keyPoints: [
      'Q4 budget review required',
      'Marketing budget increase of 15%',
      'New hiring budget for engineering',
      'Infrastructure costs for data center'
    ],
    actionItems: [
      'Schedule meeting this week',
      'Review budget proposals',
      'Prepare for board presentation'
    ],
    sentiment: 'neutral',
    urgency: 8,
    suggestedResponse: 'Hi Sarah, Thanks for reaching out. I can meet Wednesday at 2 PM to discuss the Q4 budget items. I\'ll review the proposals beforehand. Let me know if this works for you. Best regards.'
  },
  {
    id: '3',
    emailId: '3',
    summary: 'Mike Chen has concerns about project milestone timeline due to testing issues that may delay launch.',
    keyPoints: [
      'Second milestone deadline approaching',
      'Testing phase revealed issues',
      'Launch date may be pushed back',
      'Timeline adjustment needed'
    ],
    actionItems: [
      'Schedule call tomorrow morning',
      'Review testing issues',
      'Adjust project timeline if needed'
    ],
    sentiment: 'negative',
    urgency: 7,
    suggestedResponse: 'Hi Mike, I understand your concerns about the timeline. Let\'s schedule a call tomorrow at 9 AM to discuss the testing issues and explore solutions. We can work together to minimize any delays. Thanks for bringing this to my attention.'
  }
];

export const mockReminders: Reminder[] = [
  {
    id: '1',
    title: 'Follow up on Q4 budget meeting',
    description: 'Send budget proposal summary to Sarah Johnson',
    dueDate: new Date(Date.now() + 2 * 24 * 60 * 60 * 1000), // 2 days from now
    priority: 'high',
    completed: false,
    emailId: '1',
    type: 'followup'
  },
  {
    id: '2',
    title: 'Project timeline review call',
    description: 'Discuss testing issues with Mike Chen',
    dueDate: new Date(Date.now() + 16 * 60 * 60 * 1000), // tomorrow morning
    priority: 'high',
    completed: false,
    emailId: '3',
    type: 'meeting'
  },
  {
    id: '3',
    title: 'Submit monthly report',
    description: 'Prepare and submit the monthly performance report',
    dueDate: new Date(Date.now() + 5 * 24 * 60 * 60 * 1000), // 5 days from now
    priority: 'medium',
    completed: false,
    type: 'deadline'
  }
];

export const mockCalendarEvents: CalendarEvent[] = [
  {
    id: '1',
    title: 'Q4 Budget Review Meeting',
    description: 'Discuss budget allocations with Finance team',
    startTime: new Date(Date.now() + 3 * 24 * 60 * 60 * 1000), // 3 days from now
    endTime: new Date(Date.now() + 3 * 24 * 60 * 60 * 1000 + 60 * 60 * 1000), // 1 hour later
    attendees: ['sarah.johnson@techcorp.com', 'you@company.com'],
    location: 'Conference Room B',
    type: 'meeting'
  },
  {
    id: '2',
    title: 'Project Review Call',
    description: 'Address timeline concerns with client',
    startTime: new Date(Date.now() + 16 * 60 * 60 * 1000), // tomorrow morning
    endTime: new Date(Date.now() + 16 * 60 * 60 * 1000 + 30 * 60 * 1000), // 30 minutes later
    attendees: ['mike.chen@clientcompany.com', 'you@company.com'],
    type: 'call'
  }
];