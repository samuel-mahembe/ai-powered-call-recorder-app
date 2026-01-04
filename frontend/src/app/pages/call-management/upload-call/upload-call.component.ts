import { Component, ViewChild, ElementRef, OnDestroy } from "@angular/core";

import { interval, Subscription } from "rxjs";
import jsPDF from "jspdf";
import { UploadCallService } from "../../../services/upload-call.service";
import { MatCardModule } from "@angular/material/card";
import { MatButtonModule } from "@angular/material/button";
import { MatIconModule } from "@angular/material/icon";
import { MatProgressBarModule } from "@angular/material/progress-bar";
import { MatProgressSpinnerModule } from "@angular/material/progress-spinner";
import { MatDividerModule } from "@angular/material/divider";
import { MatListModule } from "@angular/material/list";
import {MatChip, MatChipsModule} from "@angular/material/chips";
import { MatTooltipModule } from "@angular/material/tooltip";
import { CommonModule } from "@angular/common";

interface CallSummary {
  call_id: string;
  summary: string[];
  sentiment: string;
  category: string;
  action_items: string[];
  customer_requests: string[];
  resolution_status: string;
  priority: string;
  tags: string[];
  agent_performance: string;
  follow_up_required: boolean;
  processed_at: string;
}

interface TranscriptResult {
  call_id: string;
  transcript: string;
  audio_duration: number;
  processed_at: string;
}

interface TranscriptMessage {
  time: string;
  speaker: 'Agent' | 'Customer';
  message: string;
}

@Component({
  selector: "app-upload-call",
  imports: [
    MatCardModule,
    MatButtonModule,
    MatIconModule,
    MatProgressBarModule,
    MatProgressSpinnerModule,
    MatListModule,
    MatDividerModule,
    MatChipsModule,
    MatChip,
    MatTooltipModule,
    CommonModule,
  ],
  templateUrl: "./upload-call.component.html",
  styleUrls: ["./upload-call.component.scss"],
})
export class UploadCallComponent implements OnDestroy {
  @ViewChild("fileInput") fileInput!: ElementRef<HTMLInputElement>;

  selectedFile: File | null = null;
  isDropzoneActive = false;
  isUploading = false;
  isProcessing = false;
  processingStatus = "50% of the call has been transcribed.";
  callResult: CallSummary | null = null;
  transcriptResult: TranscriptResult | null = null;
  parsedTranscript: TranscriptMessage[] = [];

  private pollingSub?: Subscription;
  private processingUrl: string = "";

  constructor(private uploadService: UploadCallService) {}

  onFileSelected(event: Event) {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length) {
      this.selectedFile = input.files[0];
    }
  }

  onFileDrop(event: DragEvent) {
    event.preventDefault();
    this.isDropzoneActive = false;
    if (event.dataTransfer && event.dataTransfer.files.length) {
      this.selectedFile = event.dataTransfer.files[0];
    }
  }

  onDragOver(event: DragEvent) {
    event.preventDefault();
    this.isDropzoneActive = true;
  }

  onDragLeave(event: DragEvent) {
    event.preventDefault();
    this.isDropzoneActive = false;
  }

  removeFile() {
    this.selectedFile = null;
    if (this.fileInput) {
      this.fileInput.nativeElement.value = "";
    }
  }

  uploadFile() {
    if (!this.selectedFile) return;
    this.isUploading = true;
    this.isProcessing = false;
    this.processingStatus = "";
    this.callResult = null;
    this.transcriptResult = null;

    // HARDCODED SAMPLE DATA - API CALLS COMMENTED OUT
    // Simulate processing delay
    setTimeout(() => {
      this.isUploading = false;
      this.isProcessing = true;
      this.processingStatus = "Processing audio...";
      
      // Simulate processing completion after a short delay
      setTimeout(() => {
        this.isProcessing = false;
        this.callResult = this.getHardcodedCallResult();
        this.transcriptResult = this.getHardcodedTranscriptResult();
        this.parseTranscript();
      }, 2000);
    }, 1000);

    // ORIGINAL API CALL CODE (COMMENTED OUT)
    // this.uploadService.uploadCall(this.selectedFile).subscribe({
    //   next: (res) => {
    //     this.isUploading = false;
    //     this.isProcessing = true;
    //     this.processingStatus = res.message || "Processing audio...";
    //     this.processingUrl = res.processing_url;
    //     this.startPolling();
    //   },
    //   error: (err) => {
    //     this.isUploading = false;
    //     this.processingStatus = "Upload failed. Please try again.";
    //   },
    // });
  }

  // ORIGINAL POLLING CODE (COMMENTED OUT)
  // startPolling() {
  //   if (!this.processingUrl) return;
  //   this.pollingSub = interval(2000).subscribe(() => {
  //     this.uploadService.getProcessingStatus(this.processingUrl).subscribe({
  //       next: (res) => {
  //         if (res.status && res.status !== "completed") {
  //           this.processingStatus = res.message || "Processing...";
  //         } else {
  //           this.isProcessing = false;
  //           this.callResult = res as CallSummary;
  //           this.pollingSub?.unsubscribe();
  //           this.fetchTranscript(this.callResult.call_id);
  //         }
  //       },
  //       error: () => {
  //         this.processingStatus = "Error checking status. Retrying...";
  //       },
  //     });
  //   });
  // }

  // ORIGINAL FETCH TRANSCRIPT CODE (COMMENTED OUT)
  // fetchTranscript(callId: string) {
  //   this.uploadService.getTranscript(callId).subscribe({
  //     next: (res) => (this.transcriptResult = res as TranscriptResult),
  //     error: () => (this.transcriptResult = null),
  //   });
  // }

  // HARDCODED SAMPLE DATA METHODS
  getHardcodedCallResult(): CallSummary {
    return {
      call_id: "CALL-2024-001234",
      summary: [
        "Customer called regarding a billing discrepancy on their monthly statement",
        "Agent successfully identified the issue as a double charge for service upgrade",
        "Refund of $49.99 processed immediately with confirmation email sent",
        "Customer expressed satisfaction with the resolution and service quality"
      ],
      sentiment: "positive",
      category: "Billing Inquiry",
      action_items: [
        "Verify refund processing within 3-5 business days",
        "Follow up with customer via email to confirm refund receipt",
        "Review billing system to prevent similar double-charge issues"
      ],
      customer_requests: [
        "Requested refund for duplicate charge",
        "Asked for confirmation email with transaction details",
        "Wanted assurance that this won't happen again"
      ],
      resolution_status: "resolved",
      priority: "high",
      tags: ["billing", "refund", "customer-satisfaction", "urgent"],
      agent_performance: "Agent demonstrated excellent problem-solving skills, maintained professional and empathetic tone throughout the call, and efficiently resolved the issue. Customer satisfaction score: 9/10.",
      follow_up_required: true,
      processed_at: new Date().toISOString()
    };
  }

  getHardcodedTranscriptResult(): TranscriptResult {
    return {
      call_id: "CALL-2024-001234",
      transcript: `[00:00] Agent: Thank you for calling Customer Support. This is Sarah speaking. How can I assist you today?

[00:05] Customer: Hi Sarah, I'm calling about my monthly bill. I noticed there's a duplicate charge on my statement, and I'm really concerned about this.

[00:15] Agent: I understand your concern, and I'm here to help resolve this for you. Can you please provide me with your account number or the phone number associated with your account?

[00:22] Customer: Sure, it's 555-1234.

[00:25] Agent: Thank you. I can see your account now. I notice there are two charges of $49.99 for a service upgrade that occurred on the same day. Is that the duplicate charge you're referring to?

[00:35] Customer: Yes, exactly! I only authorized one upgrade, not two. This is very frustrating.

[00:40] Agent: I completely understand your frustration, and I apologize for this error. Let me investigate this right away and get it resolved for you.

[00:48] Agent: I can see that this was indeed a system error that caused a duplicate charge. I'm processing a full refund of $49.99 to your original payment method right now. You should see the refund reflected in your account within 3-5 business days.

[01:05] Customer: Thank you so much! That's a relief. Will I receive any confirmation?

[01:10] Agent: Absolutely. I'm sending you a confirmation email right now with all the transaction details and the refund information. You should receive it within the next few minutes.

[01:20] Customer: Perfect. I really appreciate your help, Sarah. This has been resolved much faster than I expected.

[01:28] Agent: You're very welcome! I'm glad I could help resolve this for you today. Is there anything else I can assist you with?

[01:35] Customer: No, that's all. Thank you again!

[01:38] Agent: Thank you for calling, and have a wonderful day!`,
      audio_duration: 98,
      processed_at: new Date().toISOString()
    };
  }

  exportToPDF() {
    if (!this.callResult) return;
    const doc = new jsPDF();
    const pageWidth = doc.internal.pageSize.getWidth();
    const pageHeight = doc.internal.pageSize.getHeight();
    const margin = 15;
    const contentWidth = pageWidth - (margin * 2);
    let y = margin;

    // Helper function to add new page if needed
    const checkNewPage = (requiredSpace: number) => {
      if (y + requiredSpace > pageHeight - margin) {
        doc.addPage();
        y = margin;
        return true;
      }
      return false;
    };

    // Helper function to get color based on value
    const getSentimentColor = (sentiment: string): [number, number, number] => {
      switch (sentiment.toLowerCase()) {
        case 'positive': return [0, 206, 182]; // success green
        case 'neutral': return [255, 174, 31]; // warning orange
        case 'negative': return [255, 102, 146]; // error pink
        default: return [0, 161, 255]; // primary blue
      }
    };

    const getPriorityColor = (priority: string): [number, number, number] => {
      switch (priority.toLowerCase()) {
        case 'high': return [255, 102, 146]; // error pink
        case 'medium': return [255, 174, 31]; // warning orange
        case 'low': return [0, 206, 182]; // success green
        default: return [0, 161, 255]; // primary blue
      }
    };

    // Header with gradient effect
    doc.setFillColor(0, 161, 255);
    doc.rect(0, 0, pageWidth, 50, 'F');
    doc.setTextColor(255, 255, 255);
    doc.setFontSize(24);
    doc.setFont('helvetica', 'bold');
    doc.text('Call Analysis Report', margin, 25);
    doc.setFontSize(10);
    doc.setFont('helvetica', 'normal');
    doc.text(`Generated: ${new Date().toLocaleString()}`, margin, 35);
    y = 60;

    // Call ID Section
    doc.setTextColor(0, 161, 255);
    doc.setFontSize(14);
    doc.setFont('helvetica', 'bold');
    doc.text('Call Information', margin, y);
    y += 8;

    doc.setDrawColor(0, 161, 255);
    doc.setLineWidth(0.5);
    doc.line(margin, y, pageWidth - margin, y);
    y += 8;

    doc.setTextColor(0, 0, 0);
    doc.setFontSize(11);
    doc.setFont('helvetica', 'normal');
    
    const callInfo = [
      ['Call ID', this.callResult.call_id],
      ['Category', this.callResult.category],
      ['Processed At', new Date(this.callResult.processed_at).toLocaleString()]
    ];

    callInfo.forEach(([label, value]) => {
      doc.setFont('helvetica', 'bold');
      doc.text(`${label}:`, margin, y);
      doc.setFont('helvetica', 'normal');
      const textWidth = doc.getTextWidth(`${label}: `);
      doc.text(value, margin + textWidth, y);
      y += 7;
    });

    y += 5;

    // Key Metrics Section
    checkNewPage(60);
    doc.setFillColor(248, 250, 253);
    doc.roundedRect(margin, y, contentWidth, 50, 3, 3, 'F');
    
    doc.setTextColor(0, 161, 255);
    doc.setFontSize(14);
    doc.setFont('helvetica', 'bold');
    doc.text('Key Metrics', margin + 5, y + 8);
    y += 15;

    const metrics = [
      { label: 'Sentiment', value: this.callResult.sentiment, color: getSentimentColor(this.callResult.sentiment) },
      { label: 'Priority', value: this.callResult.priority, color: getPriorityColor(this.callResult.priority) },
      { label: 'Resolution', value: this.callResult.resolution_status, color: this.callResult.resolution_status === 'resolved' ? [0, 206, 182] : [255, 174, 31] },
      { label: 'Follow Up', value: this.callResult.follow_up_required ? 'Required' : 'Not Required', color: this.callResult.follow_up_required ? [255, 102, 146] : [0, 206, 182] }
    ];

    const metricBoxWidth = (contentWidth - 20) / 2;
    let metricX = margin + 5;
    let metricY = y;

    metrics.forEach((metric, index) => {
      if (index > 0 && index % 2 === 0) {
        metricX = margin + 5;
        metricY += 15;
      }

      // Metric box with lighter background
      const lightColor = [
        Math.min(255, metric.color[0] + 200),
        Math.min(255, metric.color[1] + 200),
        Math.min(255, metric.color[2] + 200)
      ];
      doc.setFillColor(lightColor[0], lightColor[1], lightColor[2]);
      doc.roundedRect(metricX, metricY, metricBoxWidth - 5, 12, 2, 2, 'F');

      doc.setFontSize(9);
      doc.setFont('helvetica', 'bold');
      doc.setTextColor(metric.color[0], metric.color[1], metric.color[2]);
      doc.text(metric.label, metricX + 3, metricY + 4);
      
      doc.setFontSize(10);
      doc.setFont('helvetica', 'normal');
      doc.setTextColor(0, 0, 0);
      doc.text(metric.value, metricX + 3, metricY + 9);

      if (index % 2 === 0) {
        metricX += metricBoxWidth;
      }
    });

    y = metricY + 20;

    // Tags Section
    if (this.callResult.tags && this.callResult.tags.length > 0) {
      checkNewPage(20);
      doc.setTextColor(0, 161, 255);
      doc.setFontSize(11);
      doc.setFont('helvetica', 'bold');
      doc.text('Tags:', margin, y);
      doc.setFont('helvetica', 'normal');
      doc.setTextColor(0, 0, 0);
      
      let tagX = margin + 15;
      let tagY = y;
      this.callResult.tags.forEach((tag, index) => {
        const tagWidth = doc.getTextWidth(tag) + 6;
        if (tagX + tagWidth > pageWidth - margin) {
          tagX = margin + 15;
          tagY += 8;
          checkNewPage(8);
        }
        doc.setFillColor(230, 240, 255);
        doc.roundedRect(tagX, tagY - 4, tagWidth, 6, 2, 2, 'F');
        doc.setFontSize(9);
        doc.text(tag, tagX + 3, tagY);
        tagX += tagWidth + 3;
      });
      y = tagY + 12;
    }

    // Summary Section
    checkNewPage(40);
    doc.setTextColor(0, 161, 255);
    doc.setFontSize(14);
    doc.setFont('helvetica', 'bold');
    doc.text('Summary', margin, y);
    y += 8;
    doc.setDrawColor(0, 161, 255);
    doc.line(margin, y, pageWidth - margin, y);
    y += 8;

    doc.setTextColor(0, 0, 0);
    doc.setFontSize(10);
    doc.setFont('helvetica', 'normal');
    
    (this.callResult.summary || []).forEach((item) => {
      checkNewPage(10);
      doc.setFillColor(0, 161, 255);
      doc.circle(margin + 3, y - 2, 2, 'F');
      const lines = doc.splitTextToSize(item, contentWidth - 20);
      doc.text(lines, margin + 10, y);
      y += lines.length * 5 + 3;
    });

    y += 5;

    // Action Items Section
    checkNewPage(40);
    doc.setTextColor(0, 206, 182);
    doc.setFontSize(14);
    doc.setFont('helvetica', 'bold');
    doc.text('Action Items', margin, y);
    y += 8;
    doc.setDrawColor(0, 206, 182);
    doc.line(margin, y, pageWidth - margin, y);
    y += 8;

    doc.setTextColor(0, 0, 0);
    doc.setFontSize(10);
    doc.setFont('helvetica', 'normal');
    
    (this.callResult.action_items || []).forEach((item) => {
      checkNewPage(10);
      doc.setFillColor(0, 206, 182);
      doc.circle(margin + 3, y - 2, 2, 'F');
      const lines = doc.splitTextToSize(item, contentWidth - 20);
      doc.text(lines, margin + 10, y);
      y += lines.length * 5 + 3;
    });

    y += 5;

    // Customer Requests Section
    checkNewPage(40);
    doc.setTextColor(22, 205, 199);
    doc.setFontSize(14);
    doc.setFont('helvetica', 'bold');
    doc.text('Customer Requests', margin, y);
    y += 8;
    doc.setDrawColor(22, 205, 199);
    doc.line(margin, y, pageWidth - margin, y);
    y += 8;

    doc.setTextColor(0, 0, 0);
    doc.setFontSize(10);
    doc.setFont('helvetica', 'normal');
    
    (this.callResult.customer_requests || []).forEach((item) => {
      checkNewPage(10);
      doc.setFillColor(22, 205, 199);
      doc.circle(margin + 3, y - 2, 2, 'F');
      const lines = doc.splitTextToSize(item, contentWidth - 20);
      doc.text(lines, margin + 10, y);
      y += lines.length * 5 + 3;
    });

    y += 5;

    // Agent Performance Section
    checkNewPage(50);
    doc.setFillColor(248, 250, 253);
    doc.roundedRect(margin, y, contentWidth, 35, 3, 3, 'F');
    
    doc.setTextColor(0, 161, 255);
    doc.setFontSize(14);
    doc.setFont('helvetica', 'bold');
    doc.text('Agent Performance', margin + 5, y + 8);
    y += 12;

    doc.setTextColor(0, 0, 0);
    doc.setFontSize(10);
    doc.setFont('helvetica', 'normal');
    const performanceLines = doc.splitTextToSize(this.callResult.agent_performance, contentWidth - 20);
    doc.text(performanceLines, margin + 5, y);
    y += performanceLines.length * 5 + 10;

    // Footer on each page
    const addFooter = (pageNum: number) => {
      doc.setFontSize(8);
      doc.setTextColor(128, 128, 128);
      doc.text(`Page ${pageNum}`, pageWidth / 2, pageHeight - 10, { align: 'center' });
    };

    // Add footer to all pages
    const totalPages = doc.internal.pages.length - 1;
    for (let i = 1; i <= totalPages; i++) {
      doc.setPage(i);
      addFooter(i);
    }

    doc.save(`call-analysis-${this.callResult.call_id}.pdf`);
  }

  exportTranscriptToPDF() {
    if (!this.transcriptResult || !this.parsedTranscript.length) return;
    const doc = new jsPDF();
    const pageWidth = doc.internal.pageSize.getWidth();
    const pageHeight = doc.internal.pageSize.getHeight();
    const margin = 15;
    const contentWidth = pageWidth - (margin * 2);
    let y = margin;

    // Helper function to add new page if needed
    const checkNewPage = (requiredSpace: number) => {
      if (y + requiredSpace > pageHeight - margin - 20) {
        doc.addPage();
        y = margin;
        return true;
      }
      return false;
    };

    // Header with gradient effect
    doc.setFillColor(0, 161, 255);
    doc.rect(0, 0, pageWidth, 50, 'F');
    doc.setTextColor(255, 255, 255);
    doc.setFontSize(24);
    doc.setFont('helvetica', 'bold');
    doc.text('Call Transcript', margin, 25);
    doc.setFontSize(10);
    doc.setFont('helvetica', 'normal');
    doc.text(`Generated: ${new Date().toLocaleString()}`, margin, 35);
    y = 60;

    // Call Information Section
    doc.setTextColor(0, 161, 255);
    doc.setFontSize(14);
    doc.setFont('helvetica', 'bold');
    doc.text('Call Information', margin, y);
    y += 8;

    doc.setDrawColor(0, 161, 255);
    doc.setLineWidth(0.5);
    doc.line(margin, y, pageWidth - margin, y);
    y += 8;

    doc.setTextColor(0, 0, 0);
    doc.setFontSize(11);
    doc.setFont('helvetica', 'normal');
    
    const callInfo = [
      ['Call ID', this.transcriptResult.call_id],
      ['Audio Duration', `${this.transcriptResult.audio_duration} seconds`],
      ['Processed At', new Date(this.transcriptResult.processed_at).toLocaleString()]
    ];

    callInfo.forEach(([label, value]) => {
      doc.setFont('helvetica', 'bold');
      doc.text(`${label}:`, margin, y);
      doc.setFont('helvetica', 'normal');
      const textWidth = doc.getTextWidth(`${label}: `);
      doc.text(value, margin + textWidth, y);
      y += 7;
    });

    y += 10;

    // Transcript Section Header
    doc.setTextColor(0, 161, 255);
    doc.setFontSize(14);
    doc.setFont('helvetica', 'bold');
    doc.text('Conversation Transcript', margin, y);
    y += 8;
    doc.setDrawColor(0, 161, 255);
    doc.line(margin, y, pageWidth - margin, y);
    y += 10;

    // Transcript Messages
    this.parsedTranscript.forEach((msg) => {
      checkNewPage(30);

      const isAgent = msg.speaker === 'Agent';
      const speakerColor = isAgent ? [0, 161, 255] : [22, 205, 199]; // Blue for agent, Teal for customer
      const bgColor = isAgent ? [0, 161, 255] : [22, 205, 199];
      const messagePadding = 8;
      const messageMargin = isAgent ? 0 : 30; // Right margin for customer messages

      // Speaker header with light background
      const lightBgColor = [
        Math.min(255, bgColor[0] + 180),
        Math.min(255, bgColor[1] + 180),
        Math.min(255, bgColor[2] + 180)
      ];
      doc.setFillColor(lightBgColor[0], lightBgColor[1], lightBgColor[2]);
      doc.roundedRect(margin + messageMargin, y, contentWidth - messageMargin, 8, 2, 2, 'F');

      doc.setFontSize(10);
      doc.setFont('helvetica', 'bold');
      doc.setTextColor(speakerColor[0], speakerColor[1], speakerColor[2]);
      doc.text(msg.speaker.toUpperCase(), margin + messageMargin + 5, y + 5);
      
      doc.setFontSize(8);
      doc.setFont('helvetica', 'normal');
      doc.setTextColor(128, 128, 128);
      const timeWidth = doc.getTextWidth(msg.time);
      doc.text(msg.time, pageWidth - margin - timeWidth - 5, y + 5);
      
      y += 10;

      // Message content box
      doc.setFillColor(bgColor[0], bgColor[1], bgColor[2]);
      // doc.Alpha(0.08);
      doc.roundedRect(margin + messageMargin, y, contentWidth - messageMargin, 0, 3, 3, 'F');
      // doc.setAlpha(1);

      // Message text
      doc.setFontSize(10);
      doc.setFont('helvetica', 'normal');
      doc.setTextColor(0, 0, 0);
      const messageLines = doc.splitTextToSize(msg.message, contentWidth - messageMargin - messagePadding * 2);
      
      // Calculate message box height
      const messageHeight = messageLines.length * 5 + messagePadding * 2;
      doc.setFillColor(bgColor[0], bgColor[1], bgColor[2]);
      // doc.setAlpha(0.08);
      doc.roundedRect(margin + messageMargin, y, contentWidth - messageMargin, messageHeight, 3, 3, 'F');
      // doc.setAlpha(1);

      doc.text(messageLines, margin + messageMargin + messagePadding, y + messagePadding + 4);
      y += messageHeight + 8;

      // Add separator line
      doc.setDrawColor(200, 200, 200);
      doc.setLineWidth(0.2);
      doc.line(margin, y, pageWidth - margin, y);
      y += 5;
    });

    // Footer on each page
    const addFooter = (pageNum: number) => {
      doc.setFontSize(8);
      doc.setTextColor(128, 128, 128);
      doc.text(`Page ${pageNum}`, pageWidth / 2, pageHeight - 10, { align: 'center' });
    };

    // Add footer to all pages
    const totalPages = doc.internal.pages.length - 1;
    for (let i = 1; i <= totalPages; i++) {
      doc.setPage(i);
      addFooter(i);
    }

    doc.save(`call-transcript-${this.transcriptResult.call_id}.pdf`);
  }

  parseTranscript() {
    if (!this.transcriptResult) return;
    
    this.parsedTranscript = [];
    const lines = this.transcriptResult.transcript.split('\n').filter(line => line.trim());
    
    lines.forEach(line => {
      const timeMatch = line.match(/\[(\d+:\d+)\]/);
      if (!timeMatch) return;
      
      const time = timeMatch[1];
      const remaining = line.substring(timeMatch[0].length).trim();
      
      if (remaining.startsWith('Agent:')) {
        this.parsedTranscript.push({
          time,
          speaker: 'Agent',
          message: remaining.substring(6).trim()
        });
      } else if (remaining.startsWith('Customer:')) {
        this.parsedTranscript.push({
          time,
          speaker: 'Customer',
          message: remaining.substring(9).trim()
        });
      }
    });
  }

  ngOnDestroy() {
    this.pollingSub?.unsubscribe();
  }
}
