import { Component } from '@angular/core';
import { MaterialModule } from '../../material.module';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';
import { CommonModule } from '@angular/common';

interface SentimentItem {
  category: string;
  count: number;
  percentage: number;
  sentiment: 'positive' | 'neutral' | 'negative';
}

@Component({
  selector: 'app-top-sentiments',
  imports: [MaterialModule, MatCardModule, MatIconModule, MatChipsModule, CommonModule],
  templateUrl: './top-sentiments.component.html',
})
export class AppTopSentimentsComponent {
  topSentiments: SentimentItem[] = [
    { category: 'Billing Inquiry', count: 342, percentage: 27.4, sentiment: 'positive' },
    { category: 'Technical Support', count: 298, percentage: 23.9, sentiment: 'positive' },
    { category: 'Product Information', count: 187, percentage: 15.0, sentiment: 'neutral' },
    { category: 'Complaint', count: 156, percentage: 12.5, sentiment: 'negative' },
    { category: 'Account Management', count: 134, percentage: 10.7, sentiment: 'positive' },
    { category: 'Refund Request', count: 130, percentage: 10.4, sentiment: 'neutral' },
  ];

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

  getSentimentIcon(sentiment: string): string {
    switch (sentiment) {
      case 'positive':
        return 'sentiment_satisfied';
      case 'neutral':
        return 'sentiment_neutral';
      case 'negative':
        return 'sentiment_dissatisfied';
      default:
        return 'help';
    }
  }
}

