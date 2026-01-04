import { Component, ViewEncapsulation } from '@angular/core';
import { MaterialModule } from '../../material.module';
import { AppTotalCallsComponent } from 'src/app/components/total-calls/total-calls.component';
import { AppSentimentDistributionComponent } from 'src/app/components/sentiment-distribution/sentiment-distribution.component';
import { AppCallTrendsComponent } from 'src/app/components/call-trends/call-trends.component';
import { AppAgentPerformanceComponent } from 'src/app/components/agent-performance/agent-performance.component';
import { AppTopSentimentsComponent } from 'src/app/components/top-sentiments/top-sentiments.component';
import { AppCallMetricsComponent } from 'src/app/components/call-metrics/call-metrics.component';

@Component({
  selector: 'app-starter',
  imports: [
    MaterialModule,
    AppTotalCallsComponent,
    AppSentimentDistributionComponent,
    AppCallTrendsComponent,
    AppAgentPerformanceComponent,
    AppTopSentimentsComponent,
    AppCallMetricsComponent,
  ],
  templateUrl: './starter.component.html',
  styleUrls: ['./starter.component.scss'],
  encapsulation: ViewEncapsulation.None,
})
export class StarterComponent { }
