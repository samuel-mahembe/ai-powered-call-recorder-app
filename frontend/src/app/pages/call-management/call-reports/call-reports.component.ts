import { Component, OnInit } from '@angular/core';
import { MaterialModule } from '../../../material.module';
import { MatCardModule } from '@angular/material/card';
import { MatTableModule } from '@angular/material/table';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { CallDetailsDialogComponent } from './call-details-dialog/call-details-dialog.component';

export interface CallRecord {
  callId: string;
  customerName: string;
  phoneNumber: string;
  agentName: string;
  date: Date;
  duration: number; // in seconds
  sentiment: 'positive' | 'neutral' | 'negative';
  category: string;
  priority: 'high' | 'medium' | 'low';
  resolutionStatus: 'resolved' | 'unresolved';
  followUpRequired: boolean;
}

@Component({
  selector: 'app-call-reports',
  imports: [
    MaterialModule,
    MatCardModule,
    MatTableModule,
    MatButtonModule,
    MatIconModule,
    MatChipsModule,
    MatDialogModule,
    MatTooltipModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    FormsModule,
    CommonModule,
  ],
  templateUrl: './call-reports.component.html',
  styleUrl: './call-reports.component.scss',
})
export class CallReportsComponent implements OnInit {
  displayedColumns: string[] = [
    'callId',
    'customerName',
    'agentName',
    'date',
    'duration',
    'sentiment',
    'category',
    'priority',
    'resolutionStatus',
    'actions',
  ];

  callRecords: CallRecord[] = [];

  // Filter options
  selectedSentiment: string = 'all';
  selectedCategory: string = 'all';
  selectedPriority: string = 'all';
  searchTerm: string = '';

  constructor(public dialog: MatDialog) {}

  ngOnInit() {
    this.loadCallRecords();
  }

  loadCallRecords() {
    // Sample call records data
    this.callRecords = [
      {
        callId: 'CALL-2024-001234',
        customerName: 'John Smith',
        phoneNumber: '+1 (555) 123-4567',
        agentName: 'Sarah Johnson',
        date: new Date('2024-01-15T10:30:00'),
        duration: 245,
        sentiment: 'positive',
        category: 'Billing Inquiry',
        priority: 'high',
        resolutionStatus: 'resolved',
        followUpRequired: true,
      },
      {
        callId: 'CALL-2024-001235',
        customerName: 'Emily Rodriguez',
        phoneNumber: '+1 (555) 234-5678',
        agentName: 'Michael Chen',
        date: new Date('2024-01-15T11:15:00'),
        duration: 180,
        sentiment: 'positive',
        category: 'Technical Support',
        priority: 'medium',
        resolutionStatus: 'resolved',
        followUpRequired: false,
      },
      {
        callId: 'CALL-2024-001236',
        customerName: 'David Kim',
        phoneNumber: '+1 (555) 345-6789',
        agentName: 'Sarah Johnson',
        date: new Date('2024-01-15T12:00:00'),
        duration: 320,
        sentiment: 'negative',
        category: 'Cancellation Request',
        priority: 'high',
        resolutionStatus: 'unresolved',
        followUpRequired: true,
      },
      {
        callId: 'CALL-2024-001237',
        customerName: 'Jessica Martinez',
        phoneNumber: '+1 (555) 456-7890',
        agentName: 'Emily Rodriguez',
        date: new Date('2024-01-15T13:20:00'),
        duration: 195,
        sentiment: 'neutral',
        category: 'Product Information',
        priority: 'low',
        resolutionStatus: 'resolved',
        followUpRequired: false,
      },
      {
        callId: 'CALL-2024-001238',
        customerName: 'Robert Taylor',
        phoneNumber: '+1 (555) 567-8901',
        agentName: 'Michael Chen',
        date: new Date('2024-01-15T14:45:00'),
        duration: 280,
        sentiment: 'positive',
        category: 'Account Management',
        priority: 'medium',
        resolutionStatus: 'resolved',
        followUpRequired: false,
      },
      {
        callId: 'CALL-2024-001239',
        customerName: 'Lisa Anderson',
        phoneNumber: '+1 (555) 678-9012',
        agentName: 'Sarah Johnson',
        date: new Date('2024-01-15T15:30:00'),
        duration: 165,
        sentiment: 'neutral',
        category: 'Refund Request',
        priority: 'medium',
        resolutionStatus: 'resolved',
        followUpRequired: true,
      },
      {
        callId: 'CALL-2024-001240',
        customerName: 'James Wilson',
        phoneNumber: '+1 (555) 789-0123',
        agentName: 'Emily Rodriguez',
        date: new Date('2024-01-15T16:10:00'),
        duration: 220,
        sentiment: 'positive',
        category: 'Billing Inquiry',
        priority: 'high',
        resolutionStatus: 'resolved',
        followUpRequired: false,
      },
      {
        callId: 'CALL-2024-001241',
        customerName: 'Maria Garcia',
        phoneNumber: '+1 (555) 890-1234',
        agentName: 'Michael Chen',
        date: new Date('2024-01-15T17:00:00'),
        duration: 310,
        sentiment: 'negative',
        category: 'Complaint',
        priority: 'high',
        resolutionStatus: 'unresolved',
        followUpRequired: true,
      },
    ];
  }

  get filteredCallRecords(): CallRecord[] {
    return this.callRecords.filter((call) => {
      const matchesSentiment = this.selectedSentiment === 'all' || call.sentiment === this.selectedSentiment;
      const matchesCategory = this.selectedCategory === 'all' || call.category === this.selectedCategory;
      const matchesPriority = this.selectedPriority === 'all' || call.priority === this.selectedPriority;
      const matchesSearch =
        this.searchTerm === '' ||
        call.customerName.toLowerCase().includes(this.searchTerm.toLowerCase()) ||
        call.callId.toLowerCase().includes(this.searchTerm.toLowerCase()) ||
        call.agentName.toLowerCase().includes(this.searchTerm.toLowerCase());

      return matchesSentiment && matchesCategory && matchesPriority && matchesSearch;
    });
  }

  formatDuration(seconds: number): string {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
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

  getPriorityColor(priority: string): string {
    switch (priority) {
      case 'high':
        return 'warn';
      case 'medium':
        return 'accent';
      case 'low':
        return 'primary';
      default:
        return '';
    }
  }

  openCallDetails(call: CallRecord) {
    const dialogRef = this.dialog.open(CallDetailsDialogComponent, {
      width: '800px',
      maxWidth: '90vw',
      maxHeight: '90vh',
      data: call,
      panelClass: 'call-details-dialog',
    });
  }
}
