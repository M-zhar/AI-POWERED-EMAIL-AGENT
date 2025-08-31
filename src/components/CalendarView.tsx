import React from 'react';
import { CalendarEvent } from '../types/email';
import { Calendar, Clock, MapPin, Users } from 'lucide-react';

interface CalendarViewProps {
  events: CalendarEvent[];
}

const CalendarView: React.FC<CalendarViewProps> = ({ events }) => {
  const formatTime = (date: Date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const formatDate = (date: Date) => {
    const today = new Date();
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);

    if (date.toDateString() === today.toDateString()) {
      return 'Today';
    } else if (date.toDateString() === tomorrow.toDateString()) {
      return 'Tomorrow';
    } else {
      return date.toLocaleDateString();
    }
  };

  const getEventTypeColor = (type: string) => {
    switch (type) {
      case 'meeting': return 'border-blue-300 bg-blue-50';
      case 'call': return 'border-green-300 bg-green-50';
      case 'event': return 'border-purple-300 bg-purple-50';
      case 'reminder': return 'border-orange-300 bg-orange-50';
      default: return 'border-gray-300 bg-gray-50';
    }
  };

  const sortedEvents = [...events].sort((a, b) => a.startTime.getTime() - b.startTime.getTime());

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-bold text-gray-900 flex items-center">
          <Calendar className="w-6 h-6 mr-2 text-blue-600" />
          Upcoming Events
        </h2>
        <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
          Add Event
        </button>
      </div>

      {sortedEvents.length === 0 ? (
        <div className="text-center py-12">
          <Calendar className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-600">No upcoming events</p>
          <p className="text-sm text-gray-500 mt-1">Your calendar is clear!</p>
        </div>
      ) : (
        <div className="space-y-4">
          {sortedEvents.map((event) => (
            <div
              key={event.id}
              className={`border-l-4 p-4 rounded-r-lg ${getEventTypeColor(event.type)}`}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h3 className="font-semibold text-gray-900 mb-1">{event.title}</h3>
                  <p className="text-sm text-gray-600 mb-3">{event.description}</p>
                  
                  <div className="flex flex-wrap items-center gap-4 text-sm text-gray-500">
                    <div className="flex items-center">
                      <Calendar className="w-4 h-4 mr-1" />
                      {formatDate(event.startTime)}
                    </div>
                    <div className="flex items-center">
                      <Clock className="w-4 h-4 mr-1" />
                      {formatTime(event.startTime)} - {formatTime(event.endTime)}
                    </div>
                    {event.location && (
                      <div className="flex items-center">
                        <MapPin className="w-4 h-4 mr-1" />
                        {event.location}
                      </div>
                    )}
                    {event.attendees.length > 0 && (
                      <div className="flex items-center">
                        <Users className="w-4 h-4 mr-1" />
                        {event.attendees.length} attendees
                      </div>
                    )}
                  </div>

                  {event.attendees.length > 0 && (
                    <div className="mt-3">
                      <p className="text-xs font-medium text-gray-700 mb-1">Attendees:</p>
                      <div className="flex flex-wrap gap-1">
                        {event.attendees.map((attendee, index) => (
                          <span
                            key={index}
                            className="px-2 py-1 bg-white bg-opacity-70 rounded-full text-xs text-gray-600"
                          >
                            {attendee}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
                
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                  event.type === 'meeting' ? 'bg-blue-100 text-blue-700' :
                  event.type === 'call' ? 'bg-green-100 text-green-700' :
                  event.type === 'event' ? 'bg-purple-100 text-purple-700' :
                  'bg-orange-100 text-orange-700'
                }`}>
                  {event.type}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default CalendarView;