import { Component } from '@angular/core';
import { MaterialModule } from '../../material.module';
import { MatCardModule } from '@angular/material/card';
import { MatTableModule } from '@angular/material/table';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';
import { CommonModule } from '@angular/common';

export interface AgentData {
  name: string;
  totalCalls: number;
  positiveSentiment: number;
  avgResolutionTime: string;
  resolutionRate: number;
  status: 'excellent' | 'good' | 'needs-improvement';
}

const AGENT_DATA: AgentData[] = [
  {
    name: 'Sarah Johnson',
    totalCalls: 245,
    positiveSentiment: 78,
    avgResolutionTime: '4.2 min',
    resolutionRate: 92,
    status: 'excellent',
  },
  {
    name: 'Michael Chen',
    totalCalls: 198,
    positiveSentiment: 72,
    avgResolutionTime: '5.1 min',
    resolutionRate: 88,
    status: 'good',
  },
  {
    name: 'Emily Rodriguez',
    totalCalls: 223,
    positiveSentiment: 81,
    avgResolutionTime: '3.8 min',
    resolutionRate: 95,
    status: 'excellent',
  },
  {
    name: 'David Kim',
    totalCalls: 187,
    positiveSentiment: 65,
    avgResolutionTime: '6.5 min',
    resolutionRate: 75,
    status: 'needs-improvement',
  },
  {
    name: 'Jessica Martinez',
    totalCalls: 211,
    positiveSentiment: 76,
    avgResolutionTime: '4.8 min',
    resolutionRate: 89,
    status: 'good',
  },
];

@Component({
  selector: 'app-agent-performance',
  imports: [MaterialModule, MatCardModule, MatTableModule, MatIconModule, MatChipsModule, CommonModule],
  templateUrl: './agent-performance.component.html',
})
export class AppAgentPerformanceComponent {
  displayedColumns: string[] = ['name', 'totalCalls', 'positiveSentiment', 'avgResolutionTime', 'resolutionRate', 'status'];
  dataSource = AGENT_DATA;

  getStatusColor(status: string): string {
    switch (status) {
      case 'excellent':
        return 'primary';
      case 'good':
        return 'accent';
      case 'needs-improvement':
        return 'warn';
      default:
        return '';
    }
  }

  getStatusLabel(status: string): string {
    switch (status) {
      case 'excellent':
        return 'Excellent';
      case 'good':
        return 'Good';
      case 'needs-improvement':
        return 'Needs Improvement';
      default:
        return status;
    }
  }
}

