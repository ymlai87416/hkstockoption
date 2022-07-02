import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { HttpModule } from '@angular/http';
import { HttpClientModule } from '@angular/common/http';

import { AppComponent } from './app.component';
import { HeaderComponent } from './header/header.component';
import { HeaderItemComponent } from './header/header-item.component';
import { HomeScreenComponent } from './home-screen/home-screen.component';
import { OptionDetailsQueryFormComponent } from './option-details/option-details-query-form/option-details-query-form.component'
import { OptionListComponent } from './option-details/option-list/option-list.component';
import { StockSummaryComponent } from './option-details/stock-summary/stock-summary.component';
import { OptionDetailsScreenComponent } from './option-details/option-details-screen/option-details-screen.component';
import { ImpliedVolatilityGraphComponent } from './option-implied-volatility/implied-volatility-graph/implied-volatility-graph.component';
import { ImpliedVolatilitySummaryComponent } from './option-implied-volatility/implied-volatility-summary/implied-volatility-summary.component';
import { OptionIvQueryFormComponent } from './option-implied-volatility/option-iv-query-form/option-iv-query-form.component';
import { OptionImpliedVolatilityScreenComponent } from './option-implied-volatility/option-implied-volatility-screen/option-implied-volatility-screen.component';
import {
  RouterModule,
  Routes,
  Router
} from '@angular/router';
import {
  APP_BASE_HREF,
  LocationStrategy,
  HashLocationStrategy
} from '@angular/common';

import{
  OptionService,
  SEARCH_STOCK_BY_SEHK_CODE_URL,
  SEARCH_STOCK_BY_SEHK_CODE_WITH_PARAM_URL,
  SEARCH_STOCK_OPTION_BY_SEHK_CODE_URL,
  SEARCH_STOCK_OPTION_BY_SEHK_CODE_WITH_PARAM_URL,
  SEARCH_STOCK_OPTION_BY_TICKER_URL,
  SEARCH_STOCK_OPTION_BY_TICKER_WITH_PARAM_URL,
  GET_UNDERLYING_ASSET_LIST_URL,
  SEARCH_IV_SERIES_BY_SEHK_CODE_URL, 
  SEARCH_IV_SERIES_BY_SEHK_CODE_WITH_PARAM_URL,
  SEARCH_STOCK_OPTION_BY_HKATS_CODE_URL, 
  SEARCH_STOCK_OPTION_BY_HKATS_CODE_WITH_PARAM_URL,
} from './option-service.service'

import { ScreenDef } from './screen.model';
import { SuiModule } from 'ng2-semantic-ui';

const screens: ScreenDef[] = [
  {label: 'Home',                            name: 'Root',                       path: '',                       component: HomeScreenComponent},
  {label: 'Option details',                  name: 'Option details',             path: 'option-details',         component: OptionDetailsScreenComponent },
  {label: 'Option implied volatility',       name: 'Option IV',                  path: 'option-iv',              component: OptionImpliedVolatilityScreenComponent},
];

const routes: Routes = [
  { path: '', component: HomeScreenComponent, pathMatch: 'full' },
  { path: 'option-details', component: OptionDetailsScreenComponent, pathMatch: 'full' },
  { path: 'option-iv', component: OptionImpliedVolatilityScreenComponent, pathMatch: 'full' },
]

@NgModule({
  declarations: [
    AppComponent,
    HeaderComponent,
    HeaderItemComponent,
    HomeScreenComponent,
    OptionDetailsQueryFormComponent,
    OptionListComponent,
    StockSummaryComponent,
    OptionDetailsScreenComponent,
    ImpliedVolatilityGraphComponent,
    ImpliedVolatilitySummaryComponent,
    OptionIvQueryFormComponent,
    OptionImpliedVolatilityScreenComponent,
  ],
  imports: [
    BrowserModule,
    RouterModule.forRoot(routes),
    HttpModule,
    HttpClientModule,
    FormsModule,
    SuiModule,
  ],
  providers: [
    {provide: OptionService, useClass: OptionService},
    { provide: APP_BASE_HREF, useValue: '/' },
    { provide: LocationStrategy, useClass: HashLocationStrategy },
    { provide: 'ScreenDefs', useValue: screens },
    { provide: SEARCH_STOCK_BY_SEHK_CODE_URL, useValue: SEARCH_STOCK_BY_SEHK_CODE_URL },
    { provide: SEARCH_STOCK_BY_SEHK_CODE_WITH_PARAM_URL, useValue: SEARCH_STOCK_BY_SEHK_CODE_WITH_PARAM_URL },
    { provide: SEARCH_STOCK_OPTION_BY_SEHK_CODE_URL, useValue: SEARCH_STOCK_OPTION_BY_SEHK_CODE_URL },
    { provide: SEARCH_STOCK_OPTION_BY_SEHK_CODE_WITH_PARAM_URL, useValue: SEARCH_STOCK_OPTION_BY_SEHK_CODE_WITH_PARAM_URL },
    { provide: SEARCH_STOCK_OPTION_BY_TICKER_URL, useValue: SEARCH_STOCK_OPTION_BY_TICKER_URL },
    { provide: SEARCH_STOCK_OPTION_BY_TICKER_WITH_PARAM_URL, useValue: SEARCH_STOCK_OPTION_BY_TICKER_WITH_PARAM_URL },
    { provide: GET_UNDERLYING_ASSET_LIST_URL, useValue: GET_UNDERLYING_ASSET_LIST_URL },
    { provide: SEARCH_IV_SERIES_BY_SEHK_CODE_URL, useValue: SEARCH_IV_SERIES_BY_SEHK_CODE_URL },
    { provide: SEARCH_IV_SERIES_BY_SEHK_CODE_WITH_PARAM_URL, useValue: SEARCH_IV_SERIES_BY_SEHK_CODE_WITH_PARAM_URL },
    { provide: SEARCH_STOCK_OPTION_BY_HKATS_CODE_URL, useValue: SEARCH_STOCK_OPTION_BY_HKATS_CODE_URL },
    { provide: SEARCH_STOCK_OPTION_BY_HKATS_CODE_WITH_PARAM_URL, useValue: SEARCH_STOCK_OPTION_BY_HKATS_CODE_WITH_PARAM_URL },
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
