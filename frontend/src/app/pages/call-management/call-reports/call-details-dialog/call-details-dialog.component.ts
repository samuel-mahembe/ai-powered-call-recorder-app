import { Component, Inject } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogModule, MatDialogRef } from '@angular/material/dialog';
import { MaterialModule } from '../../../../material.module';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';
import { MatDividerModule } from '@angular/material/divider';
import { MatListModule } from '@angular/material/list';
import { CommonModule } from '@angular/common';
import { CallRecord } from '../call-reports.component';

@Component({
  selector: 'app-call-details-dialog',
  imports: [
    MaterialModule,
    MatDialogModule,
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatChipsModule,
    MatDividerModule,
    MatListModule,
    CommonModule,
  ],
  templateUrl: './call-details-dialog.component.html',
  styleUrls: ['./call-details-dialog.component.scss'],
})
export class CallDetailsDialogComponent {
  call: CallRecord;
  callAnalysis: any;

  constructor(
    public dialogRef: MatDialogRef<CallDetailsDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: CallRecord
  ) {
    this.call = data;
    this.callAnalysis = this.generateAnalysis();
  }

  formatDuration(seconds: number): string {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins} min ${secs} sec`;
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

  generateAnalysis() {
    // Generate analysis based on call data
    const analyses: any = {
      'CALL-2024-001234': {
        summary: [
          'Customer called regarding duplicate charge on billing statement',
          'Agent identified and processed refund of $49.99',
          'Customer expressed satisfaction with resolution',
        ],
        actionItems: [
          'Verify refund processing within 3-5 business days',
          'Send confirmation email to customer',
          'Review billing system to prevent similar issues',
        ],
        customerRequests: [
          'Requested refund for duplicate charge',
          'Asked for confirmation email with transaction details',
        ],
        agentPerformance: 'Agent demonstrated excellent problem-solving skills, maintained professional and empathetic tone throughout the call, and efficiently resolved the issue. Customer satisfaction score: 9/10.',
        tags: ['billing', 'refund', 'resolved', 'satisfied'],
      },
      'CALL-2024-001235': {
        summary: [
          'Customer experiencing login issues with online account',
          'Agent reset password and sent instructions via email',
          'Issue resolved successfully',
        ],
        actionItems: [
          'Follow up if customer has further login issues',
        ],
        customerRequests: [
          'Needed help accessing online account',
          'Requested password reset',
        ],
        agentPerformance: 'Agent provided clear instructions and resolved the technical issue efficiently. Good communication skills demonstrated.',
        tags: ['technical', 'password-reset', 'resolved'],
      },
      'CALL-2024-001236': {
        summary: [
          'Customer requested subscription cancellation',
          'Agent attempted retention but customer declined',
          'Cancellation processed, service active until end of billing cycle',
        ],
        actionItems: [
          'Send cancellation confirmation email',
          'Schedule follow-up call for retention opportunity',
        ],
        customerRequests: [
          'Requested subscription cancellation',
          'Declined retention offers',
        ],
        agentPerformance: 'Agent handled cancellation professionally and attempted retention appropriately. Maintained positive relationship despite cancellation.',
        tags: ['cancellation', 'retention', 'high-priority'],
      },
    };

    return analyses[this.call.callId] || {
      summary: ['Call analysis data not available'],
      actionItems: [],
      customerRequests: [],
      agentPerformance: 'Analysis pending',
      tags: [],
    };
  }

  closeDialog() {
    this.dialogRef.close();
  }
}

