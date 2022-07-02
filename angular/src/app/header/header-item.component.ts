import {
    Component,
    OnInit,
    Input
  } from '@angular/core';
  import { ScreenDef } from '../screen.model';
  import { Location } from '@angular/common';
  import {
    Router,
    ActivatedRoute
  } from '@angular/router';
  
  @Component({
    selector: 'app-header-item',
    templateUrl: './header-item.component.html'
  })
  export class HeaderItemComponent implements OnInit {
    @Input('item') item: ScreenDef;
  
    constructor(private router: Router,
                private route: ActivatedRoute,
                private location: Location) {
    }
  
    // Checks if this current example is the selected one
    isActive(): boolean {
      return `/${this.item.path}` === this.location.path();
    }
  
    ngOnInit() {
    }
  
  }
  