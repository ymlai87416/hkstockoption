import { Component, OnInit, Input, ViewChild, ElementRef } from '@angular/core';
import { IVSeries } from '../../option-result.model';
import { Chart } from 'chart.js';
import * as moment from 'moment';

@Component({
  selector: 'app-implied-volatility-graph',
  templateUrl: './implied-volatility-graph.component.html',
  styleUrls: ['./implied-volatility-graph.component.css']
})
export class ImpliedVolatilityGraphComponent implements OnInit {

  @Input() 
  set ivseriesResult(ivseriesList: IVSeries[]){
    let ivseries;
    if (ivseriesList != null)
      ivseries = ivseriesList.find(x => x.seriesName.includes("IV"));
    else ivseries= null;
    
    if(ivseries != null){
      let orderedTimepoint = ivseries.timePointList.sort((a, b) => a.date.getTime() - b.date.getTime());
      let ivseriesDate = orderedTimepoint.map(x => this.formatChartDate(x.date));
      let ivseriesData = orderedTimepoint.map(x => x.value);

      //console.log(ivseriesDate);

      /*
      var in_canvas = document.getElementById('chart_holder');
      //remove canvas if present
      while (in_canvas.hasChildNodes()) {
        in_canvas.removeChild(in_canvas.lastChild);
      } 
      //insert canvas
      var newDiv = document.createElement('canvas');
      in_canvas.appendChild(newDiv);
      newDiv.id = "myChart";
      */

      console.log(this.canvasRef);
      if(this.chart != null) 
        this.chart.destroy();
        
      this.chart = new Chart(this.canvasRef.nativeElement.getContext('2d'), {
        type: 'line',
        data: {
          labels: ivseriesDate,
          datasets: [
            { 
              data: ivseriesData,
              borderColor: "#3cba9f",
              fill: false
            },
          ]
        },
        options: {
          legend: {
            display: false
          },
          scales: {
            xAxes: [{
              display: true
            }],
            yAxes: [{
              display: true
            }],
          }, 
          hover: {mode: null},
        }
      });
    }
  }

  formatChartDate(date: Date): string{
    return moment(date).format('DDMMM');
  }

  chart: Chart;
  
  @ViewChild('canvas') canvasRef: ElementRef;

  constructor() { 
  }

  ngOnInit() {
  }

}
