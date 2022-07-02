import { Component, Inject } from '@angular/core';
import { Router } from '@angular/router';
import { ScreenDef } from './screen.model';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {
  title = 'Toxic lab stock option analyser';

  constructor(
    private router: Router,
    @Inject('ScreenDefs') public examples: ScreenDef[]) {
  }
}
