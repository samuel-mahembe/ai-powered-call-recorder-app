import { Component } from '@angular/core';
import { MaterialModule } from '../../material.module';
import { MatCardModule } from '@angular/material/card';
import { MatIconModule } from '@angular/material/icon';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-total-calls',
  imports: [MaterialModule, MatCardModule, MatIconModule, CommonModule],
  templateUrl: './total-calls.component.html',
})
export class AppTotalCallsComponent {
  totalCalls = 1247;
  changePercent = 12.5;
  isPositive = true;
}

