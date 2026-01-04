import { Component } from '@angular/core';
import { MaterialModule } from '../../material.module';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { CommonModule } from '@angular/common';

interface Metric {
  label: string;
  value: number | string;
  icon: string;
  color: string;
  change?: number;
  isPositive?: boolean;
}

@Component({
  selector: 'app-call-metrics',
  imports: [MaterialModule, MatCardModule, MatIconModule, CommonModule],
  templateUrl: './call-metrics.component.html',
})
export class AppCallMetricsComponent {
  metrics: Metric[] = [
    {
      label: 'Resolved Calls',
      value: 1089,
      icon: 'check_circle',
      color: 'success',
      change: 8.2,
      isPositive: true,
    },
    {
      label: 'Avg Resolution Time',
      value: '4.8 min',
      icon: 'access_time',
      color: 'primary',
      change: -12.5,
      isPositive: true,
    },
    {
      label: 'Follow-ups Required',
      value: 158,
      icon: 'notifications_active',
      color: 'warn',
      change: 5.3,
      isPositive: false,
    },

  ];

  getMetricClass(metric: Metric): string {
    return `metric-card ${metric.color}`;
  }
}

