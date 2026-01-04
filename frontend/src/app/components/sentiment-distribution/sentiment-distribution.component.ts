import { Component, ViewChild } from '@angular/core';
import { MaterialModule } from '../../material.module';
import {
  ApexChart,
  ChartComponent,
  ApexDataLabels,
  ApexLegend,
  ApexTooltip,
  ApexAxisChartSeries,
  ApexPlotOptions,
  NgApexchartsModule,
  ApexFill,
} from 'ng-apexcharts';
import { MatCardModule } from '@angular/material/card';
import { CommonModule } from '@angular/common';

export interface sentimentChart {
  series: ApexAxisChartSeries;
  chart: ApexChart;
  dataLabels: ApexDataLabels;
  plotOptions: ApexPlotOptions;
  tooltip: ApexTooltip;
  legend: ApexLegend;
  fill: ApexFill;
  colors: string[];
}

@Component({
  selector: 'app-sentiment-distribution',
  imports: [MaterialModule, NgApexchartsModule, MatCardModule, CommonModule],
  templateUrl: './sentiment-distribution.component.html',
})
export class AppSentimentDistributionComponent {
  @ViewChild('chart') chart: ChartComponent = Object.create(null);
  public sentimentChart!: Partial<sentimentChart> | any;

  constructor() {
    this.sentimentChart = {
      series: [65, 25, 10], // Positive, Neutral, Negative percentages
      chart: {
        type: 'donut',
        height: 300,
        fontFamily: 'Inter, sans-serif',
      },
      dataLabels: {
        enabled: true,
        formatter: function (val: number) {
          return val + '%';
        },
        style: {
          fontSize: '14px',
          fontWeight: 600,
        },
      },
      plotOptions: {
        pie: {
          donut: {
            size: '70%',
            labels: {
              show: true,
              name: {
                show: true,
                fontSize: '16px',
                fontWeight: 600,
                offsetY: -10,
              },
              value: {
                show: true,
                fontSize: '20px',
                fontWeight: 700,
                offsetY: 10,
                formatter: function (val: string) {
                  return val + '%';
                },
              },
              total: {
                show: true,
                label: 'Total',
                fontSize: '16px',
                fontWeight: 600,
                formatter: function () {
                  return '100%';
                },
              },
            },
          },
        },
      },
      colors: ['#00ceb6', '#ffae1f', '#ff6692'], // Success, Warning, Error
      legend: {
        show: true,
        position: 'bottom',
        fontSize: '14px',
        fontWeight: 500,
        labels: {
          colors: '#111c2d',
        },
        markers: {
          width: 12,
          height: 12,
          radius: 6,
        },
        formatter: function (seriesName: string, opts: any) {
          return seriesName + ': ' + opts.w.globals.series[opts.seriesIndex] + '%';
        },
      },
      labels: ['Positive', 'Neutral', 'Negative'],
      tooltip: {
        y: {
          formatter: function (val: number) {
            return val + '%';
          },
        },
      },
    };
  }
}

