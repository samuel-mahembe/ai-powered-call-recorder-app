import { Component, ViewChild } from '@angular/core';
import { MaterialModule } from '../../material.module';
import {
  ApexChart,
  ChartComponent,
  ApexDataLabels,
  ApexLegend,
  ApexStroke,
  ApexTooltip,
  ApexAxisChartSeries,
  ApexPlotOptions,
  NgApexchartsModule,
  ApexFill,
  ApexGrid,
  ApexXAxis,
  ApexYAxis,
  ApexMarkers,
} from 'ng-apexcharts';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { CommonModule } from '@angular/common';

export interface callTrendsChart {
  series: ApexAxisChartSeries;
  chart: ApexChart;
  dataLabels: ApexDataLabels;
  plotOptions: ApexPlotOptions;
  tooltip: ApexTooltip;
  stroke: ApexStroke;
  legend: ApexLegend;
  fill: ApexFill;
  grid: ApexGrid;
  xaxis: ApexXAxis;
  yaxis: ApexYAxis;
  markers: ApexMarkers;
  colors: string[];
}

@Component({
  selector: 'app-call-trends',
  imports: [MaterialModule, NgApexchartsModule, MatCardModule, MatButtonModule, CommonModule],
  templateUrl: './call-trends.component.html',
})
export class AppCallTrendsComponent {
  @ViewChild('chart') chart: ChartComponent = Object.create(null);
  public callTrendsChart!: Partial<callTrendsChart> | any;

  constructor() {
    this.callTrendsChart = {
      series: [
        {
          name: 'Total Calls',
          type: 'area',
          data: [120, 135, 145, 130, 155, 168, 180],
        },
        {
          name: 'Positive Sentiment',
          type: 'line',
          data: [78, 88, 94, 85, 101, 109, 117],
        },
      ],
      chart: {
        height: 350,
        type: 'line',
        fontFamily: 'Inter, sans-serif',
        toolbar: {
          show: false,
        },
        zoom: {
          enabled: false,
        },
      },
      stroke: {
        curve: 'smooth',
        width: [0, 3],
      },
      fill: {
        type: 'gradient',
        gradient: {
          shade: 'light',
          type: 'vertical',
          shadeIntensity: 0.5,
          gradientToColors: ['#00a1ff', '#00ceb6'],
          inverseColors: false,
          opacityFrom: 0.7,
          opacityTo: 0.1,
          stops: [0, 100],
        },
      },
      colors: ['#00a1ff', '#00ceb6'],
      dataLabels: {
        enabled: false,
      },
      markers: {
        size: [0, 5],
        colors: ['#00a1ff', '#00ceb6'],
        strokeColors: '#fff',
        strokeWidth: 2,
        hover: {
          size: 7,
        },
      },
      xaxis: {
        categories: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        labels: {
          style: {
            fontSize: '12px',
            fontWeight: 500,
          },
        },
      },
      yaxis: {
        labels: {
          style: {
            fontSize: '12px',
            fontWeight: 500,
          },
        },
      },
      grid: {
        borderColor: '#e0e6eb',
        strokeDashArray: 4,
      },
      legend: {
        show: true,
        position: 'top',
        fontSize: '14px',
        fontWeight: 500,
        markers: {
          width: 12,
          height: 12,
          radius: 6,
        },
      },
      tooltip: {
        shared: true,
        intersect: false,
      },
    };
  }
}

