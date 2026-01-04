import { Component, OnInit, OnDestroy } from '@angular/core';
import { MaterialModule } from '../../../material.module';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatDividerModule } from '@angular/material/divider';
import { MatListModule } from '@angular/material/list';
import { MatTooltipModule } from '@angular/material/tooltip';
import { CommonModule } from '@angular/common';
import { interval, Subscription } from 'rxjs';

interface ConversationMessage {
  speaker: 'Agent' | 'Customer';
  message: string;
  timestamp: string;
}

interface CallAnalysis {
  sentiment: 'positive' | 'neutral' | 'negative';
  category: string;
  priority: string;
  resolution_status: string;
  summary: string[];
  action_items: string[];
  tags: string[];
}

interface CustomerInfo {
  name: string;
  phone: string;
  accountId: string;
  previousCalls: number;
  lastContact: string;
}

@Component({
  selector: 'app-live-call',
  imports: [
    MaterialModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatChipsModule,
    MatProgressSpinnerModule,
    MatDividerModule,
    MatListModule,
    MatTooltipModule,
    CommonModule,
  ],
  templateUrl: './live-call.component.html',
  styleUrl: './live-call.component.scss',
})
export class LiveCallComponent implements OnInit, OnDestroy {
  // Call States
  callState: 'idle' | 'ringing' | 'active' | 'on-hold' | 'ended' | 'analyzing' = 'idle';
  isMuted = false;
  isOnHold = false;
  callDuration = 0; // in seconds
  callTimerSub?: Subscription;

  // Customer Info
  currentCustomer: CustomerInfo | null = null;

  // Conversation
  conversation: ConversationMessage[] = [];
  isTyping = false;

  // Call Analysis
  callAnalysis: CallAnalysis | null = null;
  isAnalyzing = false;

  // Sample customers for demo
  private customers: CustomerInfo[] = [
    {
      name: 'John Smith',
      phone: '+1 (555) 123-4567',
      accountId: 'ACC-2024-001',
      previousCalls: 3,
      lastContact: '2 days ago',
    },
    {
      name: 'Sarah Johnson',
      phone: '+1 (555) 234-5678',
      accountId: 'ACC-2024-002',
      previousCalls: 1,
      lastContact: '1 week ago',
    },
    {
      name: 'Michael Chen',
      phone: '+1 (555) 345-6789',
      accountId: 'ACC-2024-003',
      previousCalls: 5,
      lastContact: '3 days ago',
    },
  ];

  private currentCustomerIndex = 0;

  ngOnInit() {
    // Auto-start first call for demo
    setTimeout(() => this.receiveCall(), 1000);
  }

  ngOnDestroy() {
    this.stopTimer();
  }

  receiveCall() {
    if (this.callState !== 'idle' && this.callState !== 'ended' && this.callState !== 'analyzing') {
      return;
    }

    this.callState = 'ringing';
    this.currentCustomer = this.customers[this.currentCustomerIndex];
    this.conversation = [];
    this.callAnalysis = null;
    this.callDuration = 0;
    this.isMuted = false;
    this.isOnHold = false;

    // Simulate call being answered after 2 seconds
    setTimeout(() => {
      if (this.callState === 'ringing') {
        this.answerCall();
      }
    }, 2000);
  }

  answerCall() {
    this.callState = 'active';
    this.startTimer();
    this.addSystemMessage('Call connected');
    this.simulateConversation();
  }

  startTimer() {
    this.stopTimer();
    this.callTimerSub = interval(1000).subscribe(() => {
      this.callDuration++;
    });
  }

  stopTimer() {
    if (this.callTimerSub) {
      this.callTimerSub.unsubscribe();
      this.callTimerSub = undefined;
    }
  }

  formatTime(seconds: number): string {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  }

  toggleMute() {
    this.isMuted = !this.isMuted;
    this.addSystemMessage(this.isMuted ? 'Agent muted' : 'Agent unmuted');
  }

  toggleHold() {
    this.isOnHold = !this.isOnHold;
    this.callState = this.isOnHold ? 'on-hold' : 'active';
    this.addSystemMessage(this.isOnHold ? 'Call on hold' : 'Call resumed');
    
    if (this.isOnHold) {
      this.stopTimer();
    } else {
      this.startTimer();
    }
  }

  endCall() {
    this.callState = 'ended';
    this.stopTimer();
    this.addSystemMessage('Call ended');
    this.analyzeCall();
  }

  analyzeCall() {
    this.isAnalyzing = true;
    
    // Simulate analysis delay
    setTimeout(() => {
      this.callAnalysis = this.generateAnalysis();
      this.isAnalyzing = false;
      this.callState = 'analyzing';
    }, 3000);
  }

  nextCaller() {
    this.currentCustomerIndex = (this.currentCustomerIndex + 1) % this.customers.length;
    this.callState = 'idle';
    this.receiveCall();
  }

  simulateConversation() {
    if (!this.currentCustomer) return;

    const conversations = [
      [
        { speaker: 'Customer' as const, message: 'Hello, I need help with my billing statement.' },
        { speaker: 'Agent' as const, message: 'Hello! I\'d be happy to help you with that. Can I have your account number please?' },
        { speaker: 'Customer' as const, message: 'Sure, it\'s ' + this.currentCustomer.accountId },
        { speaker: 'Agent' as const, message: 'Thank you. I can see your account. What specific issue are you experiencing with your billing?' },
        { speaker: 'Customer' as const, message: 'I noticed there\'s a duplicate charge on my last statement.' },
        { speaker: 'Agent' as const, message: 'I understand your concern. Let me investigate that for you right away.' },
        { speaker: 'Agent' as const, message: 'I can see there was indeed a duplicate charge. I\'m processing a refund of $49.99 to your account right now.' },
        { speaker: 'Customer' as const, message: 'Thank you so much! How long will it take to process?' },
        { speaker: 'Agent' as const, message: 'The refund should appear in your account within 3-5 business days. You\'ll receive a confirmation email shortly.' },
        { speaker: 'Customer' as const, message: 'Perfect, I really appreciate your help!' },
        { speaker: 'Agent' as const, message: 'You\'re very welcome! Is there anything else I can assist you with today?' },
        { speaker: 'Customer' as const, message: 'No, that\'s all. Thank you again!' },
        { speaker: 'Agent' as const, message: 'Thank you for calling. Have a wonderful day!' },
      ],
      [
        { speaker: 'Customer' as const, message: 'Hi, I\'m having trouble accessing my account online.' },
        { speaker: 'Agent' as const, message: 'I\'m sorry to hear that. Let me help you troubleshoot this issue. Are you able to see the login page?' },
        { speaker: 'Customer' as const, message: 'Yes, but when I enter my credentials, it says invalid login.' },
        { speaker: 'Agent' as const, message: 'I see. Let me reset your password for you. You\'ll receive an email with instructions to create a new password.' },
        { speaker: 'Customer' as const, message: 'That would be great, thank you!' },
        { speaker: 'Agent' as const, message: 'The password reset email has been sent. Please check your inbox and follow the instructions.' },
        { speaker: 'Customer' as const, message: 'Got it. Thanks for your help!' },
        { speaker: 'Agent' as const, message: 'You\'re welcome! If you have any other issues, feel free to call us back.' },
      ],
      [
        { speaker: 'Customer' as const, message: 'Hello, I want to cancel my subscription.' },
        { speaker: 'Agent' as const, message: 'I\'m sorry to hear you want to cancel. Can you tell me what\'s prompting this decision?' },
        { speaker: 'Customer' as const, message: 'I\'m not using the service as much as I thought I would.' },
        { speaker: 'Agent' as const, message: 'I understand. Before we proceed with cancellation, would you be interested in hearing about our discounted plans?' },
        { speaker: 'Customer' as const, message: 'Actually, I think I just want to cancel for now.' },
        { speaker: 'Agent' as const, message: 'Of course, I respect your decision. I\'ll process the cancellation for you. Your service will remain active until the end of your current billing cycle.' },
        { speaker: 'Customer' as const, message: 'Thank you for understanding.' },
        { speaker: 'Agent' as const, message: 'You\'re welcome. Is there anything else I can help you with?' },
        { speaker: 'Customer' as const, message: 'No, that\'s all.' },
        { speaker: 'Agent' as const, message: 'Thank you for being a valued customer. Have a great day!' },
      ],
    ];

    const conversation = conversations[this.currentCustomerIndex % conversations.length];
    let messageIndex = 0;

    const addNextMessage = () => {
      if (messageIndex < conversation.length && this.callState === 'active') {
        const msg = conversation[messageIndex];
        this.addMessage(msg.speaker, msg.message);
        messageIndex++;
        
        // Random delay between messages (2-5 seconds)
        const delay = 2000 + Math.random() * 3000;
        setTimeout(addNextMessage, delay);
      }
    };

    // Start conversation after a short delay
    setTimeout(addNextMessage, 1000);
  }

  addMessage(speaker: 'Agent' | 'Customer', message: string) {
    const now = new Date();
    const timestamp = now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    this.conversation.push({ speaker, message, timestamp });
  }

  addSystemMessage(message: string) {
    const now = new Date();
    const timestamp = now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    this.conversation.push({ speaker: 'Agent', message: `[System] ${message}`, timestamp });
  }

  generateAnalysis(): CallAnalysis {
    const analyses = [
      {
        sentiment: 'positive' as const,
        category: 'Billing Inquiry',
        priority: 'high',
        resolution_status: 'resolved',
        summary: [
          'Customer called regarding duplicate charge on billing statement',
          'Agent identified and processed refund of $49.99',
          'Customer expressed satisfaction with resolution',
        ],
        action_items: [
          'Verify refund processing within 3-5 business days',
          'Send confirmation email to customer',
        ],
        tags: ['billing', 'refund', 'resolved', 'satisfied'],
      },
      {
        sentiment: 'neutral' as const,
        category: 'Technical Support',
        priority: 'medium',
        resolution_status: 'resolved',
        summary: [
          'Customer experiencing login issues with online account',
          'Agent reset password and sent instructions via email',
          'Issue resolved successfully',
        ],
        action_items: [
          'Follow up if customer has further login issues',
        ],
        tags: ['technical', 'password-reset', 'resolved'],
      },
      {
        sentiment: 'negative' as const,
        category: 'Cancellation Request',
        priority: 'high',
        resolution_status: 'unresolved',
        summary: [
          'Customer requested subscription cancellation',
          'Agent attempted retention but customer declined',
          'Cancellation processed, service active until end of billing cycle',
        ],
        action_items: [
          'Send cancellation confirmation email',
          'Schedule follow-up call for retention opportunity',
        ],
        tags: ['cancellation', 'retention', 'high-priority'],
      },
    ];

    return analyses[this.currentCustomerIndex % analyses.length];
  }

  getSentimentColor(sentiment: string): string {
    switch (sentiment) {
      case 'positive':
        return 'primary';
      case 'neutral':
        return 'accent';
      case 'negative':
        return 'warn';
      default:
        return '';
    }
  }
}
